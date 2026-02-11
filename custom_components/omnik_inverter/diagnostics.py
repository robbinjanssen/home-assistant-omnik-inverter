"""Diagnostics support for Omnik Inverter integration."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS

from .const import CONF_SERIAL, SERVICE_DEVICE, SERVICE_INVERTER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import OmnikInverterConfigEntry

TO_REDACT = {CONF_HOST, CONF_IP_ADDRESS, CONF_SERIAL}


async def async_get_config_entry_diagnostics(
    _hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        The created diagnostics object.

    """
    coordinator = entry.runtime_data

    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": {
            "device": asdict(coordinator.data[SERVICE_DEVICE]),
            "inverter": asdict(coordinator.data[SERVICE_INVERTER]),
        },
    }
