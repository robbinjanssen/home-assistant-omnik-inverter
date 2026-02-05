"""Config flow for Omnik Inverter integration."""

from __future__ import annotations

import socket
from typing import Any

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
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from omnikinverter import OmnikInverter, OmnikInverterError

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SERIAL,
    CONF_SOURCE_TYPE,
    CONF_USE_CACHE,
    CONFIGFLOW_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)


async def validate_input(user_input: dict[str, Any]) -> str | None:
    """
    Validate the given user input.

    Args:
        user_input: The user input.

    Returns:
        The host name of the inverter

    Raises:
        Exception: If the host could not be validated.
    """
    host = user_input[CONF_HOST]
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as exc:
        raise Exception(  # pylint: disable=broad-exception-raised
            "invalid_host"
        ) from exc


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
        """
        Get the options flow for this handler.

        Args:
            config_entry: The ConfigEntry instance.

        Returns:
            The created config flow.
        """
        return OmnikInverterOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input=None, errors: dict[str, str] | None = None
    ) -> FlowResult:
        """
        Handle a flow initialized by the user.

        Args:
            user_input: The input received from the user or none.
            errors: A dict containing errors or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.
        """
        errors = {}
        if user_input is not None:
            user_selection = user_input[CONF_TYPE]
            self.source_type = user_selection.lower()
            if user_selection == "HTML":
                return await self.async_step_setup_html()

            if user_selection == "TCP":
                return await self.async_step_setup_tcp()

            return await self.async_step_setup()

        list_of_types = ["Javascript", "JSON", "HTML", "TCP"]

        schema = vol.Schema({vol.Required(CONF_TYPE): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle setup flow for the JS and JSON route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.
        """
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-exception-caught
                errors["base"] = str(error)
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
        """
        Handle setup flow for the HTML`route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.
        """
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-exception-caught
                errors["base"] = str(error)
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

    async def async_step_setup_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle setup flow for the TCP route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.
        """
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    serial_number=user_input[CONF_SERIAL],
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = str(error)
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                        CONF_SERIAL: user_input[CONF_SERIAL],
                    },
                )

        return self.async_show_form(
            step_id="setup_tcp",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_SERIAL): int,
                }
            ),
            errors=errors,
        )


class OmnikInverterOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """
        Initialize options flow.

        Args:
            config_entry: The ConfigEntry instance.
        """
        self.source_type = config_entry.data[CONF_SOURCE_TYPE]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle a flow initialized by the user.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry.
        """
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = str(error)
            else:
                updated_config = {CONF_SOURCE_TYPE: self.source_type}
                for key in (CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_SERIAL):
                    if key in user_input:
                        updated_config[key] = user_input[key]

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=updated_config,
                    title=user_input.get(CONF_NAME),
                )

                options = {}
                for key in (CONF_SCAN_INTERVAL, CONF_USE_CACHE):
                    options[key] = user_input[key]
                return self.async_create_entry(title="", data=options)

        fields = {
            vol.Optional(
                CONF_NAME,
                default=self.config_entry.title,
            ): str,
            vol.Required(
                CONF_HOST,
                default=self.config_entry.data.get(CONF_HOST),
            ): str,
        }

        if self.source_type == "html":
            fields[
                vol.Required(
                    CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME)
                )
            ] = str
            fields[
                vol.Required(
                    CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD)
                )
            ] = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))
        elif self.source_type == "tcp":
            fields[
                vol.Required(
                    CONF_SERIAL, default=self.config_entry.data.get(CONF_SERIAL)
                )
            ] = int

        fields[
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            )
        ] = vol.All(vol.Coerce(int), vol.Range(min=1))
        fields[vol.Optional(CONF_USE_CACHE, default=False)] = bool

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(fields),
            errors=errors,
        )
