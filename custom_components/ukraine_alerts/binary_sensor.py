"""Binary sensors for Ukraine Alerts."""

from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DOMAIN,
    ALERT_TYPE_AIR,
    ALERT_TYPE_ARTILLERY,
    ALERT_TYPE_CHEMICAL,
    ALERT_TYPE_NUCLEAR,
    ALERT_TYPE_UNKNOWN,
    ALERT_TYPE_URBAN_FIGHTS,
    MANUFACTURER,
    THREAT_KIND_DRONE,
    THREAT_KIND_ROCKET,
    THREAT_LEVEL_RED,
    THREAT_LEVEL_YELLOW,
)
from .coordinator import (
    UkraineAlertsConfigEntry,
    UkraineAlertsDataUpdateCoordinator,
)

BINARY_SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(key=ALERT_TYPE_UNKNOWN, translation_key="unknown", icon="mdi:check-circle", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=ALERT_TYPE_AIR, translation_key="air", icon="mdi:cloud", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=ALERT_TYPE_URBAN_FIGHTS, translation_key="urban_fights", icon="mdi:pistol", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=ALERT_TYPE_ARTILLERY, translation_key="artillery", icon="mdi:tank", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=ALERT_TYPE_CHEMICAL, translation_key="chemical", icon="mdi:chemical-weapon", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=ALERT_TYPE_NUCLEAR, translation_key="nuclear", icon="mdi:nuke", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=THREAT_LEVEL_YELLOW, translation_key="yellow", icon="mdi:alert", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=THREAT_LEVEL_RED, translation_key="red", icon="mdi:alert-octagon", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=THREAT_KIND_ROCKET, translation_key="rocket", icon="mdi:rocket-launch", device_class=BinarySensorDeviceClass.SAFETY),
    BinarySensorEntityDescription(key=THREAT_KIND_DRONE, translation_key="drone", icon="mdi:drone", device_class=BinarySensorDeviceClass.SAFETY),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UkraineAlertsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up threat-level binary sensors."""
    name = config_entry.data[CONF_NAME]
    coordinator = config_entry.runtime_data
    async_add_entities(
        UkraineAlertsThreatBinarySensor(
            name, config_entry.unique_id, description, coordinator
        )
        for description in BINARY_SENSOR_TYPES
    )

class UkraineAlertsThreatBinarySensor(
    CoordinatorEntity[UkraineAlertsDataUpdateCoordinator], BinarySensorEntity
):
    """Binary sensor for a specific threat."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        name: str,
        unique_id: str,
        description: BinarySensorEntityDescription,
        coordinator: UkraineAlertsDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{unique_id}-{description.key}".lower()
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, unique_id)},
            manufacturer=MANUFACTURER,
            name=name,
            configuration_url="https://siren.pp.ua/",
        )

    @property
    @override
    def is_on(self) -> bool:
        """Return whether this threat is active."""
        key = self.entity_description.key
        if key in (THREAT_LEVEL_YELLOW, THREAT_LEVEL_RED):
            return any(t["level"] == key for t in self.coordinator.data.get("threats", []))
        if key in (THREAT_KIND_ROCKET, THREAT_KIND_DRONE):
            return bool(self.coordinator.data.get(key, []))
        return bool(self.coordinator.data.get(key, False))
