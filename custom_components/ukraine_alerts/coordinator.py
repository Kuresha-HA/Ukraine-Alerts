"""Data coordinator for Ukraine Alerts."""

import asyncio
from datetime import timedelta
import logging
from typing import Any, override

import aiohttp
from aiohttp import ClientSession
from uasiren.client import Client

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ALERT_TYPE_UNKNOWN, ALERT_TYPES, DOMAIN,
    THREAT_KIND_DRONE, THREAT_KIND_ROCKET,
    THREAT_LEVEL_RED, THREAT_LEVEL_SAFE, THREAT_LEVEL_YELLOW,
)

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(seconds=10)
type UkraineAlertsConfigEntry = ConfigEntry[UkraineAlertsDataUpdateCoordinator]

def _threat_kind(reason: str | None) -> str | None:
    """Classify a threat from the API reason text."""
    text = (reason or "").lower()
    if any(word in text for word in ("дрон", "бпла", "бплa", "drone", "uav")):
        return THREAT_KIND_DRONE
    if any(word in text for word in ("ракет", "missile", "rocket")):
        return THREAT_KIND_ROCKET
    return None

class UkraineAlertsDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Ukraine Alerts API."""
    config_entry: UkraineAlertsConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: UkraineAlertsConfigEntry, session: ClientSession) -> None:
        """Initialize."""
        self.region_id = config_entry.data[CONF_REGION]
        self.uasiren = Client(session)
        super().__init__(hass, _LOGGER, config_entry=config_entry, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    @override
    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library and preserve threat levels."""
        try:
            res = await self.uasiren.get_alerts(self.region_id)
        except aiohttp.ClientResponseError as error:
            if error.status == 429:
                retry_after = None
                if error.headers:
                    retry_after_value = error.headers.get("Retry-After")
                    if retry_after_value:
                        try:
                            retry_after = max(float(retry_after_value), 1.0)
                        except ValueError:
                            retry_after = None
                raise UpdateFailed(f"Rate limited by alerts API: {error}", retry_after=retry_after or 60) from error
            raise UpdateFailed(f"Error fetching alerts from API: {error}") from error
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            raise UpdateFailed(f"Error fetching alerts from API: {error}") from error

        if not isinstance(res, list):
            raise UpdateFailed("Unexpected response from alerts API")
        payload = res[0] if res else {}
        if not isinstance(payload, dict):
            raise UpdateFailed("Unexpected payload from alerts API")

        current: dict[str, Any] = {alert_type: False for alert_type in ALERT_TYPES}
        current.update({"threat_level": THREAT_LEVEL_SAFE, "threats": [], THREAT_KIND_ROCKET: [], THREAT_KIND_DRONE: []})
        current["last_update"] = payload.get("lastUpdate")
        if "activeAlerts" not in payload:
            raise UpdateFailed("Missing activeAlerts in alerts API response")
        alerts = payload["activeAlerts"]
        if not isinstance(alerts, list):
            raise UpdateFailed("Unexpected activeAlerts payload from alerts API")

        for alert in alerts:
            if not isinstance(alert, dict):
                _LOGGER.warning("Ignoring malformed alert payload: %s", alert)
                continue
            alert_type = alert.get("type", ALERT_TYPE_UNKNOWN)
            if not isinstance(alert_type, str) or not alert_type:
                alert_type = ALERT_TYPE_UNKNOWN
            elif alert_type not in ALERT_TYPES:
                alert_type = ALERT_TYPE_UNKNOWN
            current[alert_type] = True
            levels = alert.get("activeAlertLevels", [])
            if not isinstance(levels, list):
                continue
            for level in levels:
                if not isinstance(level, dict):
                    continue
                raw_level = str(level.get("alertLevel", "")).lower()
                if raw_level not in (THREAT_LEVEL_YELLOW, THREAT_LEVEL_RED):
                    continue
                reason = level.get("reason")
                if reason is not None and not isinstance(reason, str):
                    reason = str(reason)
                kind = _threat_kind(reason)
                threat = {"level": raw_level, "reason": reason, "created_at": level.get("createdAt"), "type": alert_type, "region_id": alert.get("regionId"), "region_type": alert.get("regionType"), "kind": kind}
                current["threats"].append(threat)
                if kind in (THREAT_KIND_ROCKET, THREAT_KIND_DRONE):
                    current[kind].append(threat)
                if raw_level == THREAT_LEVEL_RED:
                    current["threat_level"] = THREAT_LEVEL_RED
                elif current["threat_level"] == THREAT_LEVEL_SAFE:
                    current["threat_level"] = THREAT_LEVEL_YELLOW
        return current
