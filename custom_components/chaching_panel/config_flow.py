"""Config flow for ChaChing Panel."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChaChingApi, ChaChingApiError
from .const import DEFAULT_NAME, DOMAIN

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


class ChaChingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ChaChing Panel."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, DEFAULT_NAME).strip() or DEFAULT_NAME

            await self.async_set_unique_id(f"chaching_{host}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = ChaChingApi(host, session)
            try:
                status = await api.get_status()
            except ChaChingApiError:
                errors["base"] = "cannot_connect"
            else:
                version = status.get("version") if isinstance(status, dict) else None
                title = f"{name}" + (f" (fw {version})" if version else "")
                return self.async_create_entry(
                    title=title,
                    data={CONF_HOST: host, CONF_NAME: name},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )
