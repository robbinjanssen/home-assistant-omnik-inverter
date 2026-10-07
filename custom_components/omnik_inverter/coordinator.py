"""Omnik Inverter platform configuration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypedDict

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from omnikinverter import Device, Inverter, OmnikInverter
from omnikinverter.exceptions import OmnikInverterAuthError, OmnikInverterError

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SERIAL,
    CONF_SOURCE_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_DEVICE,
    SERVICE_INVERTER,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class OmnikInverterData(TypedDict):
    """Class for defining data in dict."""

    inverter: Inverter
    device: Device


class OmnikInverterDataUpdateCoordinator(DataUpdateCoordinator[OmnikInverterData]):
    """Class to manage fetching Omnik Inverter data from single endpoint."""

    config_entry: ConfigEntry
    inverter_device_id: str

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching Omnik Inverter data.

        Args:
            hass: The HomeAssistant instance.
            entry: The ConfigEntry containing the user input.

        """
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

        data = entry.data
        kwargs: dict[str, Any] = {}
        if data[CONF_SOURCE_TYPE] == "html":
            kwargs = {
                "username": data[CONF_USERNAME],
                "password": data[CONF_PASSWORD],
            }
        elif data[CONF_SOURCE_TYPE] == "tcp":
            kwargs = {"serial_number": data[CONF_SERIAL]}

        self.omnikinverter = OmnikInverter(
            host=data[CONF_HOST],
            source_type=data[CONF_SOURCE_TYPE],
            session=async_get_clientsession(hass),
            **kwargs,
        )

    async def _async_update_data(self) -> OmnikInverterData:
        """Fetch data from the omnik inverter.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.

        Returns:
            An object containing the serial number as a key, and
            the resource as a value.

        Raises:
            ConfigEntryAuthFailed: An invalid config was ued.
            UpdateFailed: An error occurred when updating the data.

        """
        try:
            data: OmnikInverterData = {
                SERVICE_INVERTER: await self.omnikinverter.inverter(),
                SERVICE_DEVICE: await self.omnikinverter.device(),
            }
        except OmnikInverterAuthError as error:
            _LOGGER.exception("Failed to authenticate with the Omnik")
            raise ConfigEntryAuthFailed from error
        except OmnikInverterError as error:
            _LOGGER.exception("Failed to connect to the Omnik")
            raise UpdateFailed(error) from error
        return data
