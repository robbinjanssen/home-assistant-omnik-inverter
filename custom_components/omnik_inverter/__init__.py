"""The Omnik Inverter integration."""
from __future__ import annotations

from typing import TypedDict

from omnikinverter import Device, Inverter, OmnikInverter

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_USE_JSON,
    DOMAIN,
    LOGGER,
    SCAN_INTERVAL,
    SERVICE_DEVICE,
    SERVICE_INVERTER,
)

PLATFORMS = (SENSOR_DOMAIN,)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Omnik Inverter from a config entry."""

    coordinator = OmnikInverterDataUpdateCoordinator(hass)
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
    ) -> None:
        """Initialize global Omnik Inverter data updater."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        self.omnikinverter = OmnikInverter(
            host=self.config_entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
            use_json=self.config_entry.options.get(CONF_USE_JSON, False),
        )

    async def _async_update_data(self) -> OmnikInverterData:
        """Fetch data from Omnik Inverter."""
        data: OmnikInverterData = {
            SERVICE_INVERTER: await self.omnikinverter.inverter(),
            SERVICE_DEVICE: await self.omnikinverter.device(),
        }

        return data
