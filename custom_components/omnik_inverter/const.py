"""Constants for the Omnik Inverter integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "omnik_inverter"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)

CONF_USE_JSON = "use json"

ATTR_ENTRY_TYPE: Final = "entry_type"
ENTRY_TYPE_SERVICE: Final = "service"

SERVICE_INVERTER: Final = "inverter"
SERVICE_DEVICE: Final = "device"

SERVICES: dict[str, str] = {
    SERVICE_INVERTER: "Inverter",
    SERVICE_DEVICE: "Device",
}
