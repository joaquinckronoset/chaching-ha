"""Service handlers for the ChaChing Panel integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .api import ChaChingApi, ChaChingApiError
from .const import (
    API_DISPLAY_BITMAP,
    API_DISPLAY_BRIGHTNESS,
    API_DISPLAY_CIRCLE,
    API_DISPLAY_CLEAR,
    API_DISPLAY_DISSOLVE,
    API_DISPLAY_GIF,
    API_DISPLAY_GRAPH,
    API_DISPLAY_LINE,
    API_DISPLAY_LOCK,
    API_DISPLAY_NUMBER,
    API_DISPLAY_PANEL,
    API_DISPLAY_PIXEL,
    API_DISPLAY_RECT,
    API_DISPLAY_TEXT,
    API_DISPLAY_UNLOCK,
    API_SOUND_PLAY,
    API_SOUND_VOLUME,
    API_SOUND_WAV,
    API_VIEW_PANEL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = "entry_id"

# Servicios registrados — listado para unregister limpio
_SERVICE_NAMES = (
    "lock",
    "unlock",
    "view_panel",
    "show_text",
    "show_number",
    "show_panel",
    "show_graph",
    "clear",
    "draw_pixel",
    "draw_line",
    "draw_rect",
    "draw_circle",
    "draw_bitmap",
    "dissolve",
    "show_gif",
    "set_brightness",
    "play_sound",
    "play_wav",
    "set_volume",
)


def _resolve_api(hass: HomeAssistant, call: ServiceCall) -> ChaChingApi:
    """Pick the ChaChingApi instance referenced by the call.

    If `entry_id` is provided, look it up. Otherwise, if there's a single
    config entry, use that one. Else raise.
    """
    entries: dict[str, dict[str, Any]] = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("No hay paneles ChaChing configurados.")

    eid = call.data.get(ENTRY_ID)
    if eid:
        bucket = entries.get(eid)
        if not bucket:
            raise HomeAssistantError(f"entry_id desconocido: {eid}")
        return bucket["api"]

    if len(entries) > 1:
        raise HomeAssistantError(
            "Hay varios paneles configurados; indica `entry_id`."
        )
    return next(iter(entries.values()))["api"]


def _payload_from(call: ServiceCall, *keys: str) -> dict[str, Any]:
    """Build a JSON payload picking provided keys (skipping None)."""
    out: dict[str, Any] = {}
    for k in keys:
        if k in call.data and call.data[k] is not None:
            out[k] = call.data[k]
    return out


async def _post(hass: HomeAssistant, call: ServiceCall, path: str, *keys: str) -> None:
    api = _resolve_api(hass, call)
    payload = _payload_from(call, *keys)
    try:
        await api.post(path, payload)
    except ChaChingApiError as err:
        raise HomeAssistantError(str(err)) from err


# Schemas (laxos — el firmware ya valida)

ENTRY_ID_SCHEMA = vol.Schema({vol.Optional(ENTRY_ID): cv.string}, extra=vol.ALLOW_EXTRA)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register all ChaChing Panel services."""

    async def svc_lock(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_LOCK)

    async def svc_unlock(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_UNLOCK)

    async def svc_view_panel(call: ServiceCall) -> None:
        await _post(hass, call, API_VIEW_PANEL, "index")

    async def svc_show_text(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_TEXT,
            "text", "x", "y", "color", "font", "align_right", "swap",
        )

    async def svc_show_number(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_NUMBER,
            "value", "x", "y", "color", "font", "align_right", "swap",
        )

    async def svc_show_panel(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_PANEL,
            "label", "value", "percent", "values",
            "color_line", "color_fill", "fill", "swap",
        )

    async def svc_show_graph(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_GRAPH,
            "values", "x", "y", "w", "h",
            "color_line", "color_fill", "fill", "swap",
        )

    async def svc_clear(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_CLEAR, "swap")

    async def svc_pixel(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_PIXEL, "x", "y", "color", "swap")

    async def svc_line(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_LINE, "x0", "y0", "x1", "y1", "color", "swap"
        )

    async def svc_rect(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_RECT, "x", "y", "w", "h", "color", "fill", "swap"
        )

    async def svc_circle(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_CIRCLE, "cx", "cy", "r", "color", "fill", "swap"
        )

    async def svc_bitmap(call: ServiceCall) -> None:
        await _post(
            hass, call, API_DISPLAY_BITMAP, "x", "y", "w", "h", "data", "swap"
        )

    async def svc_dissolve(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_DISSOLVE, "steps", "ms_per_step")

    async def svc_gif(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_GIF, "url", "loops")

    async def svc_brightness(call: ServiceCall) -> None:
        await _post(hass, call, API_DISPLAY_BRIGHTNESS, "value")

    async def svc_play_sound(call: ServiceCall) -> None:
        await _post(hass, call, API_SOUND_PLAY, "name")

    async def svc_play_wav(call: ServiceCall) -> None:
        await _post(hass, call, API_SOUND_WAV, "url")

    async def svc_volume(call: ServiceCall) -> None:
        await _post(hass, call, API_SOUND_VOLUME, "value")

    handlers = {
        "lock": svc_lock,
        "unlock": svc_unlock,
        "view_panel": svc_view_panel,
        "show_text": svc_show_text,
        "show_number": svc_show_number,
        "show_panel": svc_show_panel,
        "show_graph": svc_show_graph,
        "clear": svc_clear,
        "draw_pixel": svc_pixel,
        "draw_line": svc_line,
        "draw_rect": svc_rect,
        "draw_circle": svc_circle,
        "draw_bitmap": svc_bitmap,
        "dissolve": svc_dissolve,
        "show_gif": svc_gif,
        "set_brightness": svc_brightness,
        "play_sound": svc_play_sound,
        "play_wav": svc_play_wav,
        "set_volume": svc_volume,
    }

    for name, fn in handlers.items():
        hass.services.async_register(DOMAIN, name, fn, schema=ENTRY_ID_SCHEMA)

    _LOGGER.info("ChaChing Panel: %d servicios registrados", len(handlers))


async def async_unregister_services(hass: HomeAssistant) -> None:
    for name in _SERVICE_NAMES:
        hass.services.async_remove(DOMAIN, name)
