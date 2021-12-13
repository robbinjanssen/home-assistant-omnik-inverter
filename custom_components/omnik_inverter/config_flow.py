"""Config flow for Omnik Inverter integration."""
from __future__ import annotations

from typing import Any

from omnikinverter import OmnikInverter, OmnikInverterError
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TYPE,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SOURCE_TYPE,
    CONFIGFLOW_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class OmnikInverterFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Omnik Inverter."""

    VERSION = CONFIGFLOW_VERSION

    def __init__(self):
        """Initialize with empty source type."""
        self.source_type = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OmnikInverterOptionsFlowHandler:
        """Get the options flow for this handler."""
        return OmnikInverterOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input=None, errors: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}
        if user_input is not None:
            user_selection = user_input[CONF_TYPE]
            self.source_type = user_selection.lower()
            if user_selection == "HTML":
                return await self.async_step_setup_html()
            return await self.async_step_setup()

        list_of_types = ["Javascript", "JSON", "HTML"]

        schema = vol.Schema({vol.Required(CONF_TYPE): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup flow for the JS and JSON route."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    session=session,
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                    },
                )

        return self.async_show_form(
            step_id="setup",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )

    async def async_step_setup_html(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup flow for html route."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=session,
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="setup_html",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class OmnikInverterOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Mange the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
        )
