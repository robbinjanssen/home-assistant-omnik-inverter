"""Tests for setting up the Omnik Inverter integration."""

from typing import TYPE_CHECKING

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import DOMAIN, HTML_DATA

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


@pytest.mark.usefixtures("mock_omnikinverter")
@pytest.mark.parametrize(
    "data",
    [
        {"host": "192.168.1.10", "source_type": "javascript"},
        {"host": "192.168.1.10", "source_type": "json"},
        HTML_DATA,
        {"host": "192.168.1.10", "source_type": "tcp", "serial": 123456789},
    ],
)
async def test_setup_and_unload(hass: HomeAssistant, data: dict[str, str]) -> None:
    """Test setting up and unloading an entry for each source type."""
    entry = MockConfigEntry(domain=DOMAIN, title="Home", version=2, data=data)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.omnikinverter.session is async_get_clientsession(hass)
    assert entry.runtime_data.config_entry is entry
    assert hass.states.async_all()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_unique_id_backfilled(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test older entries get the serial number as unique ID once."""
    mock_config_entry.add_to_hass(hass)
    other = MockConfigEntry(domain=DOMAIN, title="Home", version=2, data=HTML_DATA)
    other.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.unique_id == "NLDN1234"
    assert other.unique_id is None


@pytest.mark.usefixtures("mock_omnikinverter")
@pytest.mark.parametrize(
    ("domain", "old_unique_id", "new_unique_id"),
    [
        ("binary_sensor", "Home_device_online", "01jabcdef_device_online"),
        ("binary_sensor", "home_device_online", "01jabcdef_device_online"),
        (
            "sensor",
            "01JABCDEF_inverter_solar_current_power",
            "01jabcdef_inverter_solar_current_power",
        ),
    ],
)
async def test_migrate_unique_ids(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    domain: str,
    old_unique_id: str,
    new_unique_id: str,
) -> None:
    """Test unique IDs of older versions are migrated, keeping the entity ID."""
    mock_config_entry.add_to_hass(hass)
    entity_registry = er.async_get(hass)
    old = entity_registry.async_get_or_create(
        domain,
        DOMAIN,
        old_unique_id,
        config_entry=mock_config_entry,
        suggested_object_id="home_legacy",
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    migrated = entity_registry.async_get(old.entity_id)
    assert migrated is not None
    assert migrated.unique_id == new_unique_id
    assert hass.states.get(old.entity_id) is not None
    duplicates = [
        entry
        for entry in er.async_entries_for_config_entry(
            entity_registry, mock_config_entry.entry_id
        )
        if entry.unique_id == new_unique_id
    ]
    assert len(duplicates) == 1


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_migrate_skips_existing_unique_id(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test an entity is left alone when its new unique ID is already taken."""
    mock_config_entry.add_to_hass(hass)
    entity_registry = er.async_get(hass)
    old = entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "01JABCDEF_inverter_solar_energy_today",
        config_entry=mock_config_entry,
    )
    entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "01jabcdef_inverter_solar_energy_today",
        config_entry=mock_config_entry,
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get(old.entity_id)
    assert entry is not None
    assert entry.unique_id == "01JABCDEF_inverter_solar_energy_today"


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_device_entry_type_cleared(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test devices created as a service become a regular device."""
    mock_config_entry.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=mock_config_entry.entry_id,
        identifiers={(DOMAIN, f"{mock_config_entry.entry_id}_inverter")},
        entry_type=dr.DeviceEntryType.SERVICE,
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    updated = device_registry.async_get(device.id)
    assert isinstance(updated, dr.DeviceEntry)
    assert updated.entry_type is None
