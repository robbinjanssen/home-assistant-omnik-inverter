"""The Omnik Inverter integration."""
from __future__ import annotations

from datetime import timedelta
from typing import TypedDict

from omnikinverter import Device, Inverter, OmnikInverter
from omnikinverter.exceptions import OmnikInverterError

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SOURCE_TYPE,
    CONFIGFLOW_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    SERVICE_DEVICE,
    SERVICE_INVERTER,
)

PLATFORMS = (SENSOR_DOMAIN,)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Omnik Inverter from a config entry."""

    scan_interval = timedelta(
        minutes=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    coordinator = OmnikInverterDataUpdateCoordinator(hass, scan_interval)
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await coordinator.omnikinverter.close()
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.omnikinverter.close()

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    if config_entry.version <= 2:
        LOGGER.warning(
            "Impossible to migrate config version from version %s to version %s.\r\nPlease consider to delete and re-add the integration.",
            config_entry.version,
            CONFIGFLOW_VERSION,
        )
        return False


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


class OmnikInverterData(TypedDict):
    """Class for defining data in dict."""

    inverter: Inverter
    device: Device


class OmnikInverterDataUpdateCoordinator(DataUpdateCoordinator[OmnikInverterData]):
    """Class to manage fetching Omnik Inverter data from single endpoint."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        scan_interval: timedelta,
    ) -> None:
        """Initialize global Omnik Inverter data updater."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

        if self.config_entry.data[CONF_SOURCE_TYPE] == "html":
            self.omnikinverter = OmnikInverter(
                host=self.config_entry.data[CONF_HOST],
                source_type=self.config_entry.data[CONF_SOURCE_TYPE],
                username=self.config_entry.data[CONF_USERNAME],
                password=self.config_entry.data[CONF_PASSWORD],
                session=async_get_clientsession(hass),
            )
        else:
            self.omnikinverter = OmnikInverter(
                host=self.config_entry.data[CONF_HOST],
                source_type=self.config_entry.data[CONF_SOURCE_TYPE],
                session=async_get_clientsession(hass),
            )

    async def _async_update_data(self) -> OmnikInverterData:
        """Fetch data from Omnik Inverter."""
        try:
            data: OmnikInverterData = {
                SERVICE_INVERTER: await self.omnikinverter.inverter(),
                SERVICE_DEVICE: await self.omnikinverter.device(),
            }
            return data
        except OmnikInverterError as err:
            raise UpdateFailed(err) from err
