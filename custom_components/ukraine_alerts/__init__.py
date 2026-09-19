"""The Ukraine Alerts integration."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS
from .coordinator import UkraineAlertsConfigEntry, UkraineAlertsDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: UkraineAlertsConfigEntry
) -> bool:
    """Set up Ukraine Alerts as a config entry."""
    websession = async_get_clientsession(hass)
    coordinator = UkraineAlertsDataUpdateCoordinator(hass, entry, websession)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: UkraineAlertsConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
