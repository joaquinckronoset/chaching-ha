"""Config flow for ChaChing Panel."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import ChaChingApi, ChaChingApiError
from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


class ChaChingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ChaChing Panel."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_host: str | None = None
        self._discovered_name: str | None = None

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

        # Si venimos por zeroconf, pre-rellenar campos
        defaults: dict[str, Any] = {}
        if self._discovered_host:
            defaults[CONF_HOST] = self._discovered_host
        if self._discovered_name:
            defaults[CONF_NAME] = self._discovered_name

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, vol.UNDEFINED)): str,
                vol.Optional(
                    CONF_NAME,
                    default=defaults.get(CONF_NAME, DEFAULT_NAME),
                ): str,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> config_entries.ConfigFlowResult:
        """Handle zeroconf discovery: a ChaChing Panel just announced itself on LAN."""
        host = discovery_info.host
        props = discovery_info.properties or {}
        device_name = props.get("name") or DEFAULT_NAME
        version = props.get("version")

        # Identidad única: usar el hostname del anuncio (chaching-<mac>) si está,
        # si no, caer en el host IP.
        hostname = (discovery_info.hostname or "").rstrip(".")
        if hostname.endswith(".local"):
            hostname = hostname[: -len(".local")]
        unique_id = hostname or f"chaching_{host}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        # Mostrar contexto en el listado de descubrimientos
        title = device_name
        if version:
            title = f"{device_name} (fw {version})"
        self.context["title_placeholders"] = {
            "name": device_name,
            "host": host,
            "version": version or "?",
        }

        self._discovered_host = host
        self._discovered_name = device_name

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirmar el descubrimiento con un click."""
        if user_input is not None:
            host = self._discovered_host or ""
            name = self._discovered_name or DEFAULT_NAME

            session = async_get_clientsession(self.hass)
            api = ChaChingApi(host, session)
            try:
                status = await api.get_status()
            except ChaChingApiError:
                return self.async_abort(reason="cannot_connect")

            version = status.get("version") if isinstance(status, dict) else None
            title = f"{name}" + (f" (fw {version})" if version else "")
            return self.async_create_entry(
                title=title,
                data={CONF_HOST: host, CONF_NAME: name},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={
                "name": self._discovered_name or DEFAULT_NAME,
                "host": self._discovered_host or "",
            },
        )
