"""Config flow for Omnik Inverter integration."""

from __future__ import annotations

import socket
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TYPE,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from omnikinverter import Inverter, OmnikInverter, OmnikInverterError

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SERIAL,
    CONF_SOURCE_TYPE,
    CONFIGFLOW_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)

PASSWORD_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


class InvalidHostError(Exception):
    """Exception raised when the host is invalid."""


async def validate_input(hass: HomeAssistant, user_input: dict[str, Any]) -> str | None:
    """Validate the given user input.

    Args:
        hass: The HomeAssistant instance.
        user_input: The user input.

    Returns:
        The host name of the inverter

    Raises:
        InvalidHostError: If the host could not be validated.

    """
    host = user_input[CONF_HOST]
    try:
        return await hass.async_add_executor_job(socket.gethostbyname, host)
    except socket.gaierror as exc:
        msg = "invalid_host"
        raise InvalidHostError(msg) from exc


async def async_get_inverter(
    hass: HomeAssistant, user_input: dict[str, Any], **kwargs: Any
) -> Inverter:
    """Validate the host and fetch the inverter data.

    Args:
        hass: The HomeAssistant instance.
        user_input: The user input.
        **kwargs: Extra arguments for the Omnik Inverter client.

    Returns:
        The inverter data.

    """
    await validate_input(hass, user_input)
    client = OmnikInverter(
        host=user_input[CONF_HOST],
        session=async_get_clientsession(hass),
        **kwargs,
    )
    return await client.inverter()


class OmnikInverterFlowHandler(ConfigFlow, domain=DOMAIN):  # pylint: disable=abstract-method
    """Config flow for Omnik Inverter."""

    VERSION = CONFIGFLOW_VERSION

    def __init__(self) -> None:
        """Initialize with empty source type."""
        self.source_type: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: ConfigEntry,
    ) -> OmnikInverterOptionsFlowHandler:
        """Get the options flow for this handler.

        Args:
            _config_entry: The ConfigEntry instance.

        Returns:
            The created config flow.

        """
        return OmnikInverterOptionsFlowHandler()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user.

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
    ) -> ConfigFlowResult:
        """Handle setup flow for the JS and JSON route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.

        """
        errors = {}

        if user_input is not None:
            try:
                inverter = await async_get_inverter(
                    self.hass,
                    user_input,
                    source_type=self.source_type,
                )
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except InvalidHostError as error:
                errors["base"] = str(error)
            else:
                await self._async_set_unique_id(inverter)
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
    ) -> ConfigFlowResult:
        """Handle setup flow for the HTML route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.

        """
        errors = {}

        if user_input is not None:
            try:
                inverter = await async_get_inverter(
                    self.hass,
                    user_input,
                    source_type=self.source_type,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except InvalidHostError as error:
                errors["base"] = str(error)
            else:
                await self._async_set_unique_id(inverter)
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
                    vol.Required(CONF_PASSWORD): PASSWORD_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_setup_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle setup flow for the TCP route.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry or a form to re-enter the user input with errors.

        """
        errors = {}

        if user_input is not None:
            try:
                inverter = await async_get_inverter(
                    self.hass,
                    user_input,
                    source_type=self.source_type,
                    serial_number=user_input[CONF_SERIAL],
                )
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except InvalidHostError as error:
                errors["base"] = str(error)
            else:
                await self._async_set_unique_id(inverter)
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

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the connection settings.

        Args:
            user_input: The input received from the user or none.

        Returns:
            An abort result after updating the entry or a form with errors.

        """
        entry = self._get_reconfigure_entry()
        source_type = entry.data[CONF_SOURCE_TYPE]
        errors = {}

        if user_input is not None:
            client_kwargs: dict[str, Any] = {}
            if source_type == "html":
                client_kwargs = {
                    "username": user_input[CONF_USERNAME],
                    "password": user_input[CONF_PASSWORD],
                }
            elif source_type == "tcp":
                client_kwargs = {"serial_number": user_input[CONF_SERIAL]}

            try:
                inverter = await async_get_inverter(
                    self.hass,
                    user_input,
                    source_type=source_type,
                    **client_kwargs,
                )
            except OmnikInverterError:
                LOGGER.exception("Failed to connect to the Omnik")
                errors["base"] = "cannot_connect"
            except InvalidHostError as error:
                errors["base"] = str(error)
            else:
                if entry.unique_id and inverter.serial_number:
                    await self.async_set_unique_id(inverter.serial_number)
                    self._abort_if_unique_id_mismatch(reason="wrong_device")
                self.hass.config_entries.async_update_entry(
                    entry, data={**entry.data, **user_input}
                )
                return self.async_abort(reason="reconfigure_successful")

        fields: dict[Any, Any] = {vol.Required(CONF_HOST): str}
        if source_type == "html":
            fields[vol.Required(CONF_USERNAME)] = str
            fields[vol.Required(CONF_PASSWORD)] = PASSWORD_SELECTOR
        elif source_type == "tcp":
            fields[vol.Required(CONF_SERIAL)] = int

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(fields), user_input or entry.data
            ),
            errors=errors,
        )

    async def _async_set_unique_id(self, inverter: Inverter) -> None:
        """Abort the flow if this inverter is already configured.

        Args:
            inverter: The inverter data fetched during the flow.

        """
        if inverter.serial_number:
            await self.async_set_unique_id(inverter.serial_number)
            self._abort_if_unique_id_configured()


class OmnikInverterOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created options or the options form.

        """
        if user_input is not None:
            return self.async_create_entry(data=user_input)

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
