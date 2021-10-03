"""Constants for the Omnik Inverter integration."""
from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "omnik_inverter"
CONFIGFLOW_VERSION = 2;
LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = 4

CONF_SOURCE_TYPE = "source_type"
CONF_SCAN_INTERVAL = "scan_interval"

ATTR_ENTRY_TYPE: Final = "entry_type"
ENTRY_TYPE_SERVICE: Final = "service"

SERVICE_INVERTER: Final = "inverter"
SERVICE_DEVICE: Final = "device"

SERVICES: dict[str, str] = {
    SERVICE_INVERTER: "Inverter",
    SERVICE_DEVICE: "Device",
}
