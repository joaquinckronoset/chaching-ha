"""Thin async HTTP client for the ChaChing Panel firmware."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout

from .const import API_STATUS, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class ChaChingApiError(Exception):
    """Raised on transport / HTTP errors talking to the panel."""


class ChaChingApi:
    """Async client for the ChaChing Panel HTTP API.

    Stateless: each call uses a short-lived request through the shared session.
    """

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self._host = host.strip()
        self._session = session
        self._base = f"http://{self._host}"

    @property
    def base_url(self) -> str:
        return self._base

    async def get_status(self) -> dict[str, Any]:
        return await self._request("GET", API_STATUS)

    async def post(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._request("POST", path, payload or {})

    async def get(self, path: str) -> dict[str, Any]:
        return await self._request("GET", path)

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base}{path}"
        timeout = ClientTimeout(total=DEFAULT_TIMEOUT)
        try:
            async with self._session.request(
                method, url, json=payload, timeout=timeout
            ) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise ChaChingApiError(
                        f"{method} {path} -> HTTP {resp.status}: {text[:200]}"
                    )
                # Algunos endpoints devuelven application/octet-stream o vacío
                ctype = resp.headers.get("Content-Type", "")
                if "application/json" in ctype:
                    return await resp.json()
                return {"ok": True}
        except asyncio.TimeoutError as err:
            raise ChaChingApiError(f"timeout calling {url}") from err
        except ClientError as err:
            raise ChaChingApiError(f"transport error calling {url}: {err}") from err
