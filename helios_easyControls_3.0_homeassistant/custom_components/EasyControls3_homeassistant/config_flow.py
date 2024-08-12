"""Config flow for Hello World integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from .const import DOMAIN  # pylint:disable=unused-import
from .EasyControls3Instance import EasyControls3Instance

import ipaddress

_LOGGER = logging.getLogger(__name__)


DATA_SCHEMA = vol.Schema({("host"): str})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short hostname
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.       
    try:
        ipaddress.IPv4Network(data["host"])
    except ValueError:
         raise InvalidHost

    easyControlsInstance = EasyControls3Instance(data["host"])
    result = await easyControlsInstance.test_connection()
    if not result:
        raise CannotConnect

    return {"title": data["host"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `host` field, not the entire form.
                errors["host"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""