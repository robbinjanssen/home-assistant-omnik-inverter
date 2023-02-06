"""Omnik Inverter platform configuration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONFIGFLOW_VERSION, DOMAIN, LOGGER
from .coordinator import OmnikInverterDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up OmnikInverter as config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true after setting up.
    """
    hass.data.setdefault(DOMAIN, {})

    coordinator = OmnikInverterDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true if unload was successful, false otherwise.
    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry  # pylint: disable=unused-argument
):
    """
    Migrate an old entry.

    Args:
        hass: The HomeAssistant instance.
        config_entry: The ConfigEntry containing the user input.

    Returns:
        Return false, not possible.
    """
    if config_entry.version <= 2:
        LOGGER.warning(
            "Impossible to migrate config version from version %s to version %s.\r\nPlease consider to delete and re-add the integration.",  # noqa: E501
            config_entry.version,
            CONFIGFLOW_VERSION,
        )
        return False
