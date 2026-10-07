"""Tests for the Omnik Inverter config and options flow."""

import socket
from dataclasses import replace
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from omnikinverter import OmnikInverterConnectionError

from .conftest import DOMAIN, HTML_DATA, INVERTER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

SOURCES = [
    ("Javascript", "setup", {}, {"source_type": "javascript"}),
    ("JSON", "setup", {}, {"source_type": "json"}),
    (
        "HTML",
        "setup_html",
        {"username": "admin", "password": "secretpw"},
        {"source_type": "html", "username": "admin", "password": "secretpw"},
    ),
    ("TCP", "setup_tcp", {"serial": 1234}, {"source_type": "tcp", "serial": 1234}),
]


async def _start_flow(hass: HomeAssistant, source: str) -> str:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"type": source}
    )
    return result["flow_id"]


@pytest.mark.usefixtures("mock_omnikinverter", "mock_gethostbyname")
@pytest.mark.parametrize(("source", "step_id", "user_input", "data"), SOURCES)
async def test_create_entry(
    hass: HomeAssistant,
    source: str,
    step_id: str,
    user_input: dict[str, str],
    data: dict[str, str],
) -> None:
    """Test creating an entry for each source type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"type": source}
    )
    assert result["step_id"] == step_id

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Home", "host": "inverter.local", **user_input}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home"
    assert result["data"] == {"host": "inverter.local", **data}
    assert result["result"].unique_id == "NLDN1234"


@pytest.mark.usefixtures("mock_omnikinverter", "mock_gethostbyname")
async def test_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test the same inverter cannot be added twice."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, unique_id="NLDN1234")

    flow_id = await _start_flow(hass, "JSON")
    result = await hass.config_entries.flow.async_configure(
        flow_id, {"name": "Home", "host": "inverter.local"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_invalid_host(hass: HomeAssistant) -> None:
    """Test an unresolvable host shows an error."""
    flow_id = await _start_flow(hass, "JSON")
    with patch("socket.gethostbyname", side_effect=socket.gaierror):
        result = await hass.config_entries.flow.async_configure(
            flow_id, {"name": "Home", "host": "nope"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_host"}


@pytest.mark.usefixtures("mock_gethostbyname")
async def test_cannot_connect(hass: HomeAssistant) -> None:
    """Test a connection error shows an error."""
    flow_id = await _start_flow(hass, "JSON")
    with patch(
        "omnikinverter.OmnikInverter.inverter",
        AsyncMock(side_effect=OmnikInverterConnectionError),
    ):
        result = await hass.config_entries.flow.async_configure(
            flow_id, {"name": "Home", "host": "inverter.local"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_options_flow_reloads(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test changing the options reloads the entry with the new settings."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={"scan_interval": 4, "use_cache": True}
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    coordinator = mock_config_entry.runtime_data

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    data_schema = result["data_schema"]
    assert data_schema is not None
    assert list(data_schema.schema) == ["scan_interval"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"scan_interval": 10}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {"scan_interval": 10}
    assert mock_config_entry.runtime_data is not coordinator
    update_interval = mock_config_entry.runtime_data.update_interval
    assert update_interval is not None
    assert update_interval.total_seconds() == 600


@pytest.mark.usefixtures("mock_omnikinverter", "mock_gethostbyname")
@pytest.mark.parametrize(
    ("data", "user_input"),
    [
        (
            {"host": "192.168.1.10", "source_type": "json"},
            {"host": "192.168.1.11"},
        ),
        (
            HTML_DATA,
            {"host": "192.168.1.11", "username": "user", "password": "newpw"},
        ),
        (
            {"host": "192.168.1.10", "source_type": "tcp", "serial": 1234},
            {"host": "192.168.1.11", "serial": 5678},
        ),
    ],
)
async def test_reconfigure(
    hass: HomeAssistant, data: dict[str, Any], user_input: dict[str, Any]
) -> None:
    """Test reconfiguring the connection settings reloads the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN, title="Home", version=2, data=data, unique_id="NLDN1234"
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    coordinator = entry.runtime_data

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    data_schema = result["data_schema"]
    assert data_schema is not None
    assert list(data_schema.schema) == list(user_input)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {**data, **user_input}
    assert entry.title == "Home"
    assert entry.runtime_data is not coordinator


@pytest.mark.usefixtures("mock_gethostbyname")
async def test_reconfigure_errors(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test reconfiguring shows an error and refuses another inverter."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, unique_id="NLDN1234")
    user_input = {"host": "192.168.1.11", "username": "admin", "password": "pw"}

    result = await mock_config_entry.start_reconfigure_flow(hass)
    with patch(
        "omnikinverter.OmnikInverter.inverter",
        AsyncMock(side_effect=OmnikInverterConnectionError),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    other = replace(INVERTER, serial_number="OTHER5678")
    with patch("omnikinverter.OmnikInverter.inverter", AsyncMock(return_value=other)):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert mock_config_entry.data["host"] == "192.168.1.10"
