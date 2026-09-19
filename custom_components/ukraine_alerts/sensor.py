"""Sensors for Ukraine Alerts."""

from typing import Any, override

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER, THREAT_KIND_DRONE, THREAT_KIND_ROCKET, THREAT_LEVEL_RED, THREAT_LEVEL_SAFE, THREAT_LEVEL_YELLOW
from .coordinator import UkraineAlertsConfigEntry, UkraineAlertsDataUpdateCoordinator

SENSOR_DESCRIPTION = SensorEntityDescription(key="threat_level", translation_key="threat_level", icon="mdi:shield-alert")

async def async_setup_entry(hass: HomeAssistant, config_entry: UkraineAlertsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up the overall threat level sensor."""
    name = config_entry.data[CONF_NAME]
    coordinator = config_entry.runtime_data
    async_add_entities([UkraineAlertsThreatLevelSensor(name, config_entry.unique_id, coordinator)])

class UkraineAlertsThreatLevelSensor(CoordinatorEntity[UkraineAlertsDataUpdateCoordinator], SensorEntity):
    """Overall Ukraine Alerts threat level."""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [THREAT_LEVEL_SAFE, THREAT_LEVEL_YELLOW, THREAT_LEVEL_RED]

    def __init__(self, name: str, unique_id: str, coordinator: UkraineAlertsDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self.entity_description = SENSOR_DESCRIPTION
        self._attr_unique_id = f"{unique_id}-threat_level".lower()
        self._attr_device_info = DeviceInfo(entry_type=DeviceEntryType.SERVICE, identifiers={(DOMAIN, unique_id)}, manufacturer=MANUFACTURER, name=name, configuration_url="https://siren.pp.ua/")

    @property
    @override
    def icon(self) -> str:
        """Return an icon matching the current threat level."""
        return {THREAT_LEVEL_SAFE: "mdi:shield-check", THREAT_LEVEL_YELLOW: "mdi:alert", THREAT_LEVEL_RED: "mdi:alert-octagon"}.get(self.native_value, "mdi:shield-alert")

    @property
    @override
    def native_value(self) -> str:
        """Return the overall threat level."""
        return self.coordinator.data.get("threat_level", "safe")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed active threats."""
        data = self.coordinator.data
        threats = data.get("threats", [])
        rocket = data.get(THREAT_KIND_ROCKET, [])
        drone = data.get(THREAT_KIND_DRONE, [])
        level = data.get("threat_level", THREAT_LEVEL_SAFE)
        level_names = {
            "safe": {"uk": "безпечний", "ru": "безопасный", "en": "safe", "de": "sicher", "hu": "biztonságos", "it": "sicuro", "fr": "sûr", "es": "seguro", "pt": "seguro", "be": "бяспечны", "pl": "bezpieczny", "cs": "bezpečný", "sk": "bezpečný", "ro": "sigur", "nl": "veilig"},
            "yellow": {"uk": "жовтий", "ru": "жёлтый", "en": "yellow", "de": "gelb", "hu": "sárga", "it": "giallo", "fr": "jaune", "es": "amarillo", "pt": "amarelo", "be": "жоўты", "pl": "żółty", "cs": "žlutý", "sk": "žltý", "ro": "galben", "nl": "geel"},
            "red": {"uk": "червоний", "ru": "красный", "en": "red", "de": "rot", "hu": "vörös", "it": "rosso", "fr": "rouge", "es": "rojo", "pt": "vermelho", "be": "чырвоны", "pl": "czerwony", "cs": "červený", "sk": "červený", "ro": "roșu", "nl": "rood"},
        }
        kind_names = {
            THREAT_KIND_ROCKET: {"uk": "Ракетна загроза", "ru": "Ракетная угроза", "en": "Rocket threat", "de": "Raketenbedrohung", "hu": "Rakétafenyegetés", "it": "Minaccia missilistica", "fr": "Menace de missiles", "es": "Amenaza de misiles", "pt": "Ameaça de mísseis", "be": "Ракетная пагроза", "pl": "Zagrożenie rakietowe", "cs": "Raketová hrozba", "sk": "Raketová hrozba", "ro": "Amenințare cu rachete", "nl": "Rakettendreiging"},
            THREAT_KIND_DRONE: {"uk": "Дронова загроза", "ru": "Дроновая угроза", "en": "Drone threat", "de": "Drohnenbedrohung", "hu": "Drónfenyegetés", "it": "Minaccia di droni", "fr": "Menace de drones", "es": "Amenaza de drones", "pt": "Ameaça de drones", "be": "Пагроза дронаў", "pl": "Zagrożenie dronowe", "cs": "Hrozba dronů", "sk": "Hrozba dronov", "ro": "Amenințare cu drone", "nl": "Dreiging door drones"},
        }
        localized = {lang: [] for lang in level_names[THREAT_LEVEL_SAFE]}
        for threat in threats:
            kind = threat.get("kind")
            reason = threat.get("reason")
            if not reason:
                continue
            for lang in localized:
                label = kind_names.get(kind, {}).get(lang, kind or threat.get("type", "Threat"))
                localized[lang].append(f"{label}: {reason}")
        return {
            "threats": threats,
            "active_reasons": [t.get("reason") for t in threats if t.get("reason")],
            "threats_uk": localized["uk"], "threats_ru": localized["ru"], "threats_en": localized["en"],
            **{f"threats_{lang}": localized[lang] for lang in localized if lang not in {"uk", "ru", "en"}},
            "threat_level_uk": level_names[level]["uk"], "threat_level_ru": level_names[level]["ru"], "threat_level_en": level_names[level]["en"],
            **{f"threat_level_{lang}": level_names[level][lang] for lang in level_names[THREAT_LEVEL_SAFE] if lang not in {"uk", "ru", "en"}},
            "yellow_active": any(t["level"] == THREAT_LEVEL_YELLOW for t in threats),
            "red_active": any(t["level"] == THREAT_LEVEL_RED for t in threats),
            "rocket_active": bool(rocket),
            "rocket_reasons": [t.get("reason") for t in rocket if t.get("reason")],
            "drone_active": bool(drone),
            "drone_reasons": [t.get("reason") for t in drone if t.get("reason")],
            "api_last_update": data.get("last_update"),
        }
