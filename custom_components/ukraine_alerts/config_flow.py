"""Config flow for Ukraine Alerts."""

import logging
from typing import TYPE_CHECKING, Any, override

import aiohttp
from uasiren.client import Client
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_REGION
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class UkraineAlertsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Ukraine Alerts."""

    VERSION = 1

    def __init__(self) -> None:
        self.states: list[dict[str, Any]] | None = None
        self.selected_region: dict[str, Any] | None = None

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if len(self._async_current_entries()) == 5:
            return self.async_abort(reason="max_regions")

        if not self.states:
            websession = async_get_clientsession(self.hass)
            reason = None
            unknown_err_msg = None
            try:
                regions = await Client(websession).get_regions()
            except aiohttp.ClientResponseError as ex:
                if ex.status == 429:
                    reason = "rate_limit"
                else:
                    reason = "unknown"
                    unknown_err_msg = str(ex)
            except aiohttp.ClientConnectionError:
                reason = "cannot_connect"
            except aiohttp.ClientError as ex:
                reason = "unknown"
                unknown_err_msg = str(ex)
            except TimeoutError:
                reason = "timeout"

            if unknown_err_msg:
                _LOGGER.error("Failed to connect to the service: %s", unknown_err_msg)

            if reason:
                return self.async_abort(reason=reason)

            if not isinstance(regions, dict):
                _LOGGER.error("Unexpected regions API response: %s", regions)
                return self.async_abort(reason="unknown")

            states = regions.get("states")
            if not isinstance(states, list):
                _LOGGER.error("Regions API response has invalid states: %s", states)
                return self.async_abort(reason="unknown")

            self.states = _normalize_regions(states)
            if not self.states:
                _LOGGER.error("Regions API returned no valid states")
                return self.async_abort(reason="unknown")

        return await self._handle_pick_region("user", "district", user_input)

    async def async_step_district(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        return await self._handle_pick_region("district", "community", user_input)

    async def async_step_community(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        return await self._handle_pick_region("community", None, user_input, True)

    async def _handle_pick_region(
        self,
        step_id: str,
        next_step: str | None,
        user_input: dict[str, str] | None,
        last_step: bool = False,
    ) -> ConfigFlowResult:
        if self.selected_region:
            source = self.selected_region.get("regionChildIds", [])
        else:
            source = self.states or []

        if not isinstance(source, list):
            _LOGGER.error("Invalid region children for config flow: %s", source)
            return self.async_abort(reason="unknown")

        if user_input is not None:
            if (
                not self.selected_region
                or user_input[CONF_REGION] != self.selected_region["regionId"]
            ):
                self.selected_region = _find(source, user_input[CONF_REGION])
                if self.selected_region is None:
                    _LOGGER.error(
                        "Selected region %s was not found in config flow data",
                        user_input[CONF_REGION],
                    )
                    return self.async_abort(reason="unknown")
                if next_step and self.selected_region["regionChildIds"]:
                    return await getattr(self, f"async_step_{next_step}")()

            return await self._async_finish_flow()

        regions = {}
        if self.selected_region and step_id != "district":
            regions[self.selected_region["regionId"]] = self.selected_region[
                "regionName"
            ]
        regions.update(_make_regions_object(source))

        schema = vol.Schema({vol.Required(CONF_REGION): vol.In(regions)})
        return self.async_show_form(
            step_id=step_id, data_schema=schema, last_step=last_step
        )

    async def _async_finish_flow(self) -> ConfigFlowResult:
        if TYPE_CHECKING:
            assert self.selected_region is not None

        await self.async_set_unique_id(self.selected_region["regionId"])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self.selected_region["regionName"],
            data={
                CONF_REGION: self.selected_region["regionId"],
                CONF_NAME: self.selected_region["regionName"],
            },
        )


def _normalize_regions(regions: list[Any]) -> list[dict[str, Any]]:
    """Return only well-formed regions and sanitize their child lists."""
    normalized: list[dict[str, Any]] = []

    for region in regions:
        if not isinstance(region, dict):
            _LOGGER.warning("Ignoring malformed region payload: %s", region)
            continue

        region_id = region.get("regionId")
        region_name = region.get("regionName")
        if not isinstance(region_id, str) or not region_id:
            _LOGGER.warning("Ignoring region with invalid regionId: %s", region)
            continue
        if not isinstance(region_name, str) or not region_name:
            _LOGGER.warning("Ignoring region with invalid regionName: %s", region_id)
            continue

        children = region.get("regionChildIds", [])
        if children is None:
            children = []
        if not isinstance(children, list):
            _LOGGER.warning(
                "Ignoring malformed regionChildIds for region %s", region_id
            )
            children = []

        normalized.append(
            {
                **region,
                "regionId": region_id,
                "regionName": region_name,
                "regionChildIds": _normalize_regions(children),
            }
        )

    return normalized


def _find(regions: list[dict[str, Any]], region_id: str) -> dict[str, Any] | None:
    """Find a region by ID without assuming API fields are valid."""
    return next(
        (region for region in regions if region.get("regionId") == region_id),
        None,
    )


def _make_regions_object(regions: list[dict[str, Any]]) -> dict[str, str]:
    """Build the config-flow selector from validated regions."""
    regions = sorted(regions, key=lambda region: region["regionName"].lower())
    return {region["regionId"]: region["regionName"] for region in regions}
