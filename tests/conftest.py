"""Fixtures for the Omnik Inverter integration tests."""

import importlib
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, PropertyMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from omnikinverter import Device, Inverter

if TYPE_CHECKING:
    from collections.abc import Generator

# Import the integration before pytest-homeassistant-custom-component imports
# its own custom_components package, so Home Assistant can find it.
importlib.import_module("custom_components.omnik_inverter")

DOMAIN = "omnik_inverter"

INVERTER = Inverter(
    serial_number="NLDN1234",
    model="omnik2000tl",
    solar_rated_power=2000,
    solar_current_power=500,
    solar_energy_today=3.2,
    solar_energy_total=1234.5,
    alarm_code="0",
    firmware="V5",
    temperature=30.0,
    solar_hours_total=100,
    dc_input_voltage=[1.0, 2.0, 3.0],
    dc_input_current=[1.0, 2.0, 3.0],
    ac_output_voltage=[1.0, 2.0, 3.0],
    ac_output_current=[1.0, 2.0, 3.0],
    ac_output_frequency=[50.0, 50.0, 50.0],
    ac_output_power=[1.0, 2.0, 3.0],
)
DEVICE = Device(signal_quality=90, firmware="H4", ip_address="192.168.1.10")

HTML_DATA = {
    "host": "192.168.1.10",
    "source_type": "html",
    "username": "admin",
    "password": "secretpw",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,  # pylint: disable=unused-argument
) -> None:
    """Enable custom integrations in all tests."""


@pytest.fixture
def mock_omnikinverter() -> Generator[None]:
    """Return inverter and device data without connecting to an inverter."""
    with (
        patch(
            "omnikinverter.OmnikInverter.inverter",
            AsyncMock(return_value=INVERTER),
        ),
        patch(
            "omnikinverter.OmnikInverter.device",
            AsyncMock(return_value=DEVICE),
        ),
    ):
        yield


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Enable all entities, including those disabled by default."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        new_callable=PropertyMock,
        return_value=True,
    ):
        yield


@pytest.fixture
def mock_gethostbyname() -> Generator[None]:
    """Resolve every host without a network lookup."""
    with patch("socket.gethostbyname", return_value="127.0.0.1"):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for an inverter using the HTML source."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        version=2,
        data=HTML_DATA,
        entry_id="01JABCDEF",
    )
