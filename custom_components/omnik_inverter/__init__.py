"""Omnik Inverter platform configuration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONFIGFLOW_VERSION, LOGGER
from .coordinator import OmnikInverterDataUpdateCoordinator

type OmnikInverterConfigEntry = ConfigEntry[OmnikInverterDataUpdateCoordinator]

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> bool:
    """Set up OmnikInverter as config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true after setting up.

    """
    coordinator = OmnikInverterDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> bool:
    """Unload a config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true if unload was successful, false otherwise.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Migrate an old entry.

    Args:
        _hass: The HomeAssistant instance.
        config_entry: The ConfigEntry containing the user input.

    Returns:
        Return false, not possible.

    """
    if config_entry.version <= 2:
        LOGGER.warning(
            "Impossible to migrate config version from version %s to version %s."
            "\r\nPlease consider to delete and re-add the integration.",
            config_entry.version,
            CONFIGFLOW_VERSION,
        )
        return False
    return False
