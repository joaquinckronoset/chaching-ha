"""DataUpdateCoordinator for ChaChing Panel."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ChaChingApi, ChaChingApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ChaChingCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls /api/status periodically so HA knows if the panel is reachable."""

    def __init__(self, hass: HomeAssistant, api: ChaChingApi, name: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}:{name}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_status()
        except ChaChingApiError as err:
            raise UpdateFailed(str(err)) from err
