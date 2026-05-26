# ChaChing Panel — Home Assistant integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Integración para Home Assistant del panel LED **ChaChing** (firmware ≥ v2.3.24, dispositivo ESP32-S3 con HUB75 64×32).

Permite, desde HA, **pausar el timeline del panel, mostrar lo que quieras, y reanudarlo** — además de exponer todos los servicios HTTP del firmware como `service`s de Home Assistant.

## Características

- **Configuración por UI** (config flow): solo IP del panel y nombre.
- **Sin auth**: el panel está en LAN, sin API key.
- **Polling ligero** del endpoint `/api/status` para conocer estado (versión firmware, brillo, volumen, lock).
- **23 servicios** que cubren todos los endpoints del firmware:
  - `chaching_panel.lock` / `unlock` — pausar/reanudar el timeline
  - `chaching_panel.show_text` / `show_number` / `show_panel` / `show_graph`
  - `chaching_panel.draw_pixel` / `draw_line` / `draw_rect` / `draw_circle` / `draw_bitmap`
  - `chaching_panel.clear` / `dissolve` / `show_gif`
  - `chaching_panel.set_brightness` / `set_volume`
  - `chaching_panel.play_sound` / `play_wav`
  - `chaching_panel.view_panel` — saltar a panel concreto del timeline

## Instalación

### Vía HACS (recomendado)

1. En HACS → Integraciones → menú ⋮ → **Custom repositories**.
2. Añade `https://github.com/joaquincaroe/chaching-ha` con categoría **Integration**.
3. Busca **ChaChing Panel** e instala.
4. Reinicia Home Assistant.
5. Ajustes → Dispositivos y servicios → **Añadir integración** → ChaChing Panel.

### Manual

Copia `custom_components/chaching_panel/` a `<config>/custom_components/` y reinicia HA.

## Configuración

Tras añadir la integración, indica:
- **Host**: IP local del panel (ej. `192.168.68.125`).
- **Nombre**: nombre del dispositivo en HA (ej. "Salón").

## Patrón típico: pausar timeline, mostrar algo, reanudar

```yaml
- alias: "Mostrar notificación timbre"
  trigger:
    - platform: state
      entity_id: binary_sensor.timbre
      to: "on"
  action:
    - service: chaching_panel.lock
      data:
        entry_id: !input chaching_entry
    - service: chaching_panel.show_text
      data:
        entry_id: !input chaching_entry
        text: "TIMBRE"
        x: 0
        y: 16
        color: red
        font: arial_18
    - delay: "00:00:10"
    - service: chaching_panel.unlock
      data:
        entry_id: !input chaching_entry
```

## Servicios

Ver `custom_components/chaching_panel/services.yaml` para la firma completa de cada servicio. Todos aceptan opcionalmente un `entry_id` para distinguir entre varios paneles configurados.

## Compatibilidad de firmware

Probado contra `firmware ChaChing v2.3.24+`. Los endpoints HTTP están en `/api/...` del puerto 80 del ESP, con CORS abierto.

## Licencia

MIT.
