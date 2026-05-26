"""The ChaChing Panel integration."""
from __future__ import annotations

import logging

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ChaChingApi
from .const import DOMAIN, PLATFORMS
from .coordinator import ChaChingCoordinator
from .services import async_register_services, async_unregister_services

_LOGGER = logging.getLogger(__name__)

# Marker para no repetir la notificación de bienvenida en cada reload
_WELCOME_FLAG = "welcome_notified"

# Dashboard YAML que el usuario puede pegar en "Raw configuration editor".
# Versión simple (sin el bloque de Ejemplos en markdown) para que la
# notificación no sea kilométrica. El completo está en example_dashboard.yaml.
_EXAMPLE_DASHBOARD_YAML = """\
title: ChaChing Test
views:
  - title: Tests rapidos
    icon: mdi:flash
    cards:
      - type: horizontal-stack
        cards:
          - type: button
            name: Texto
            icon: mdi:format-text
            tap_action:
              action: call-service
              service: chaching_panel.show_text
              data: { text: HOLA HA, x: 4, y: 22, color: cyan, font: arial_20, hold_ms: 5000 }
          - type: button
            name: Numero
            icon: mdi:numeric
            tap_action:
              action: call-service
              service: chaching_panel.show_number
              data: { value: 42, x: 18, y: 20, color: yellow, font: arial_20, hold_ms: 5000 }
          - type: button
            name: Alerta
            icon: mdi:alert
            tap_action:
              action: call-service
              service: chaching_panel.show_text
              data: { text: ALERT!, x: 4, y: 22, color: red, font: arial_20, hold_ms: 5000 }
      - type: horizontal-stack
        cards:
          - type: button
            name: Panel
            icon: mdi:chart-box-outline
            tap_action:
              action: call-service
              service: chaching_panel.show_panel
              data: { label: HA, value: 23.5, percent: 78, color_line: green, color_fill: green, hold_ms: 5000 }
          - type: button
            name: Grafica
            icon: mdi:chart-line
            tap_action:
              action: call-service
              service: chaching_panel.show_graph
              data:
                values: [10, 15, 13, 18, 22, 24, 28, 25, 30, 32, 35, 38]
                color_line: cyan
                color_fill: cyan
                hold_ms: 5000
          - type: button
            name: Limpiar
            icon: mdi:eraser
            tap_action:
              action: call-service
              service: chaching_panel.clear
  - title: Sonidos
    icon: mdi:music
    cards:
      - type: horizontal-stack
        cards:
          - type: button
            name: Order!
            icon: mdi:cash-register
            tap_action:
              action: call-service
              service: chaching_panel.play_sound
              data: { name: order }
          - type: button
            name: Coin
            icon: mdi:hand-coin
            tap_action:
              action: call-service
              service: chaching_panel.play_sound
              data: { name: coin }
          - type: button
            name: EpicWin
            icon: mdi:trophy
            tap_action:
              action: call-service
              service: chaching_panel.play_sound
              data: { name: epicwin }
          - type: button
            name: YouWin
            icon: mdi:medal
            tap_action:
              action: call-service
              service: chaching_panel.play_sound
              data: { name: youwin }
  - title: Control
    icon: mdi:tune
    cards:
      - type: horizontal-stack
        cards:
          - type: button
            name: Lock
            icon: mdi:lock
            tap_action: { action: call-service, service: chaching_panel.lock }
          - type: button
            name: Unlock
            icon: mdi:lock-open-variant
            tap_action: { action: call-service, service: chaching_panel.unlock }
      - type: horizontal-stack
        cards:
          - type: button
            name: 10%
            icon: mdi:brightness-2
            tap_action:
              action: call-service
              service: chaching_panel.set_brightness
              data: { value: 10 }
          - type: button
            name: 60%
            icon: mdi:brightness-6
            tap_action:
              action: call-service
              service: chaching_panel.set_brightness
              data: { value: 60 }
          - type: button
            name: 100%
            icon: mdi:brightness-7
            tap_action:
              action: call-service
              service: chaching_panel.set_brightness
              data: { value: 100 }
"""


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

    # Saludo + dashboard de prueba (solo la primera vez por entry)
    await _async_post_install_welcome(hass, entry, host, name, api)
    return True


async def _async_post_install_welcome(
    hass: HomeAssistant,
    entry: ConfigEntry,
    host: str,
    name: str,
    api: ChaChingApi,
) -> None:
    """Emite una persistent_notification con el dashboard de prueba y dispara
    un texto en el panel para confirmación visual inmediata. Solo se hace
    una vez por config_entry (marca con entry.options).
    """
    if entry.options.get(_WELCOME_FLAG):
        return

    # Test visual instantáneo: mostrar "HA OK" durante 8 segundos.
    # Usa hold_ms para auto-lock (firmware v2.3.34+). En firmwares más
    # antiguos hold_ms se ignora y el carousel sobreescribe inmediatamente.
    try:
        await api.post(
            "/api/display/text",
            {
                "text": "HA OK",
                "x": 4,
                "y": 22,
                "color": "cyan",
                "font": "arial_20",
                "hold_ms": 8000,
            },
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Welcome show_text failed: %s", err)

    title = f"ChaChing Panel — '{name}' añadido"
    message = (
        f"Tu panel ChaChing en `{host}` está conectado. Acabas de ver un mensaje "
        "**HA OK** en pantalla (si no, comprueba conectividad).\n\n"
        "### Dashboard de prueba\n\n"
        "Para probar los servicios con un click:\n\n"
        "1. Settings → Dashboards → **+ Add Dashboard** → *New dashboard from scratch*. "
        "Title: `ChaChing Test`, Icon: `mdi:led-strip-variant`.\n"
        "2. Abre el dashboard → menú ⋮ → **Take control**.\n"
        "3. ⋮ → **Edit dashboard** → ⋮ → **Raw configuration editor**.\n"
        "4. Borra lo que haya y pega el YAML siguiente:\n\n"
        "```yaml\n"
        f"{_EXAMPLE_DASHBOARD_YAML}"
        "```\n\n"
        "Guardar. Tendrás 8 botones (Test, Lock, Unlock, Clear + 4 sonidos) "
        "listos para probar.\n\n"
        "Más info en el [README del repo](https://github.com/joaquinckronoset/chaching-ha)."
    )
    persistent_notification.async_create(
        hass,
        message=message,
        title=title,
        notification_id=f"chaching_panel_welcome_{entry.entry_id}",
    )

    # Marca para no repetir la notificación en próximos reloads
    hass.config_entries.async_update_entry(
        entry, options={**dict(entry.options), _WELCOME_FLAG: True}
    )


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
