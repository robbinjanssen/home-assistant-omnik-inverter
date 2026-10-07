"""Tests for the Omnik Inverter diagnostics."""

from typing import TYPE_CHECKING

import pytest

from custom_components.omnik_inverter.diagnostics import (
    async_get_config_entry_diagnostics,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.mark.usefixtures("mock_omnikinverter")
async def test_diagnostics_redacted(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test credentials and identifiers are redacted."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)

    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    for secret in ("secretpw", "admin", "NLDN1234", "192.168.1.10"):
        assert secret not in str(diagnostics)
    assert diagnostics["data"]["inverter"]["solar_current_power"] == 500
    assert diagnostics["data"]["device"]["signal_quality"] == 90
