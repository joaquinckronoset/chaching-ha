"""The ChaChing Panel integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChaChingApi
from .const import DOMAIN, PLATFORMS
from .coordinator import ChaChingCoordinator
from .services import async_register_services, async_unregister_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration (services registered on first entry)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ChaChing Panel from a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)

    session = async_get_clientsession(hass)
    api = ChaChingApi(host, session)
    coordinator = ChaChingCoordinator(hass, api, name)

    # Refresh inicial: si falla, ConfigEntryNotReady haría reintentos. Mejor
    # arrancar suave para no romper si el panel está apagado.
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "name": name,
        "host": host,
    }

    # Registrar servicios una sola vez (al primer entry)
    if len(hass.data[DOMAIN]) == 1:
        await async_register_services(hass)

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = True
    if PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            await async_unregister_services(hass)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry on options change."""
    await hass.config_entries.async_reload(entry.entry_id)
