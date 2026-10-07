"""Tests for the Omnik Inverter sensors."""

from typing import TYPE_CHECKING

import pytest
from homeassistant.helpers.icon import async_get_icons

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.mark.usefixtures("mock_omnikinverter", "entity_registry_enabled_by_default")
@pytest.mark.parametrize(
    ("entity_id", "name", "state"),
    [
        (
            "binary_sensor.home_inverter_wi_fi_module_online",
            "Wi-Fi module Online",
            "on",
        ),
        (
            "sensor.home_inverter_wi_fi_module_ip_address",
            "Wi-Fi module IP address",
            "192.168.1.10",
        ),
        (
            "sensor.home_inverter_wi_fi_module_signal_quality",
            "Wi-Fi module Signal quality",
            "90",
        ),
        (
            "sensor.home_inverter_current_power_production",
            "Home Inverter Current power production",
            "500",
        ),
        (
            "sensor.home_inverter_solar_production_today",
            "Home Inverter Solar production today",
            "3.2",
        ),
        ("sensor.home_inverter_temperature", "Home Inverter Temperature", "30.0"),
        (
            "sensor.home_inverter_dc_input_1_voltage",
            "Home Inverter DC input 1 voltage",
            "1.0",
        ),
        (
            "sensor.home_inverter_ac_output_3_power",
            "Home Inverter AC output 3 power",
            "3.0",
        ),
    ],
)
async def test_entities(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_id: str,
    name: str,
    state: str,
) -> None:
    """Test the entity IDs, names and states of a new installation."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_state = hass.states.get(entity_id)
    assert entity_state is not None
    assert entity_state.name == name
    assert entity_state.state == state


@pytest.mark.usefixtures("mock_omnikinverter", "entity_registry_enabled_by_default")
async def test_entity_count_and_icons(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test all entities are created and their icons are loaded."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == 27

    icons = await async_get_icons(hass, "entity", {"omnik_inverter"})
    sensor_icons = icons["omnik_inverter"]["sensor"]
    assert sensor_icons["solar_current_power"] == {"default": "mdi:weather-sunny"}
    assert sensor_icons["ac_output_frequency"] == {"default": "mdi:sine-wave"}
