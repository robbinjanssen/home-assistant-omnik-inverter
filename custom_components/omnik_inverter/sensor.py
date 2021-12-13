"""Support for Omnik Inverter sensors."""
from __future__ import annotations

from typing import Literal

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OmnikInverterDataUpdateCoordinator
from .const import DOMAIN, MANUFACTURER, SERVICE_DEVICE, SERVICE_INVERTER, SERVICES

SENSORS: dict[Literal["inverter", "device"], tuple[SensorEntityDescription, ...]] = {
    SERVICE_INVERTER: (
        SensorEntityDescription(
            key="solar_current_power",
            name="Current Power Production",
            icon="mdi:weather-sunny",
            native_unit_of_measurement=POWER_WATT,
            device_class=DEVICE_CLASS_POWER,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        SensorEntityDescription(
            key="solar_energy_today",
            name="Solar Production - Today",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_energy_total",
            name="Solar Production - Total",
            icon="mdi:chart-line",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
    ),
    SERVICE_DEVICE: (
        SensorEntityDescription(
            key="signal_quality",
            name="Signal Quality",
            icon="mdi:wifi",
            native_unit_of_measurement=PERCENTAGE,
        ),
        SensorEntityDescription(
            key="ip_address",
            name="IP Address",
            icon="mdi:network",
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Omnik Inverter Sensors based on a config entry."""
    async_add_entities(
        OmnikInverterSensorEntity(
            coordinator=hass.data[DOMAIN][entry.entry_id],
            description=description,
            service_key=service_key,
            name=entry.title,
            service=SERVICES[service_key],
        )
        for service_key, service_sensors in SENSORS.items()
        for description in service_sensors
    )


class OmnikInverterSensorEntity(CoordinatorEntity, SensorEntity):
    """Defines an Omnik Inverter sensor."""

    coordinater: OmnikInverterDataUpdateCoordinator

    def __init__(
        self,
        *,
        coordinator: OmnikInverterDataUpdateCoordinator,
        description: SensorEntityDescription,
        service_key: Literal["inverter", "device"],
        name: str,
        service: str,
    ) -> None:
        """Initialize Omnik Inverter sensor."""
        super().__init__(coordinator=coordinator)
        self._service_key = service_key

        self.entity_id = f"{SENSOR_DOMAIN}.{name}_{description.key}"
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{service_key}_{description.key}"
        )

        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, f"{coordinator.config_entry.entry_id}_{service_key}")
            },
            name=service,
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
            sw_version=coordinator.data[service_key].firmware,
            model=coordinator.data["inverter"].model,
            configuration_url=f'http://{coordinator.data["device"].ip_address}',
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = getattr(
            self.coordinator.data[self._service_key], self.entity_description.key
        )
        if isinstance(value, str):
            return value.lower()
        return value
