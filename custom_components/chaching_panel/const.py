"""Constants for the ChaChing Panel integration."""
from __future__ import annotations

DOMAIN = "chaching_panel"
PLATFORMS: list[str] = []  # sin entities por ahora; solo services

CONF_HOST = "host"
CONF_NAME = "name"

DEFAULT_NAME = "ChaChing Panel"
DEFAULT_TIMEOUT = 5  # seconds
DEFAULT_SCAN_INTERVAL = 30  # seconds

# HTTP API paths (relativos a http://{host})
API_STATUS = "/api/status"

API_DISPLAY_LOCK = "/api/display/lock"
API_DISPLAY_UNLOCK = "/api/display/unlock"
API_DISPLAY_TEXT = "/api/display/text"
API_DISPLAY_NUMBER = "/api/display/number"
API_DISPLAY_CLEAR = "/api/display/clear"
API_DISPLAY_PIXEL = "/api/display/pixel"
API_DISPLAY_LINE = "/api/display/line"
API_DISPLAY_RECT = "/api/display/rect"
API_DISPLAY_CIRCLE = "/api/display/circle"
API_DISPLAY_BITMAP = "/api/display/bitmap"
API_DISPLAY_BRIGHTNESS = "/api/display/brightness"
API_DISPLAY_GRAPH = "/api/display/graph"
API_DISPLAY_PANEL = "/api/display/panel"
API_DISPLAY_GIF = "/api/display/gif"
API_DISPLAY_DISSOLVE = "/api/display/dissolve"
API_VIEW_PANEL = "/api/view_panel"

API_SOUND_PLAY = "/api/sound/play"
API_SOUND_WAV = "/api/sound/wav"
API_SOUND_VOLUME = "/api/sound/volume"
API_SOUND_STATUS = "/api/sound/status"
API_SOUND_LIST = "/api/sound/list"
