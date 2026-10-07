"""Tests for the Omnik Inverter config and options flow."""

import socket
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType

from omnikinverter import OmnikInverterConnectionError

from .conftest import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

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


@pytest.mark.usefixtures("mock_omnikinverter", "mock_gethostbyname")
async def test_options_flow_reloads(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test changing the options reloads the entry with the new settings."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    coordinator = mock_config_entry.runtime_data

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "name": "Zolder",
            "host": "192.168.1.11",
            "username": "admin",
            "password": "secretpw",
            "scan_interval": 10,
            "use_cache": False,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.title == "Zolder"
    assert mock_config_entry.data["host"] == "192.168.1.11"
    assert mock_config_entry.runtime_data is not coordinator
    update_interval = mock_config_entry.runtime_data.update_interval
    assert update_interval is not None
    assert update_interval.total_seconds() == 600
