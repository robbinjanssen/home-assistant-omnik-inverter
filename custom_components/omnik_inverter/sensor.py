"""Support for Omnik Inverter sensors."""
from __future__ import annotations
from dataclasses import dataclass
import dataclasses

import logging
from typing import Literal

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
    FREQUENCY_HERTZ,
    TIME_HOURS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OmnikInverterDataUpdateCoordinator
from .const import DOMAIN, MANUFACTURER, SERVICE_DEVICE, SERVICE_INVERTER, SERVICES


_LOGGER = logging.getLogger(__name__)


@dataclass
class ArraySensorEntityDescription(SensorEntityDescription):
    range: range | None = None
    data_key: str | None = None


entity_registry_enabled_default = (False,)
SENSORS: dict[Literal["inverter", "device"], tuple[SensorEntityDescription, ...]] = {
    SERVICE_INVERTER: (
        SensorEntityDescription(
            key="solar_current_power",
            name="Current Power Production",
            icon="mdi:weather-sunny",
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="solar_energy_today",
            name="Solar Production - Today",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_energy_total",
            name="Solar Production - Total",
            icon="mdi:chart-line",
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_hours_total",
            name="Solar Production - Uptime",
            icon="mdi:clock",
            native_unit_of_measurement=TIME_HOURS,
            device_class=None,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="temperature",
            name="Inverter temperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=TEMP_CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="dc_input_{}_voltage",
            data_key="dc_input_voltage",
            range=range(3),
            name="DC Input {} - Voltage",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="dc_input_{}_current",
            data_key="dc_input_current",
            range=range(3),
            name="DC Input {} - Current",
            entity_registry_enabled_default=False,
            icon="mdi:current-dc",
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="ac_output_{}_voltage",
            data_key="ac_output_voltage",
            range=range(3),
            name="AC Output {} - Voltage",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="ac_output_{}_current",
            data_key="ac_output_current",
            range=range(3),
            name="AC Output {} - Current",
            entity_registry_enabled_default=False,
            icon="mdi:current-ac",
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="ac_output_{}_power",
            data_key="ac_output_power",
            range=range(3),
            name="AC Output {} - Power",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=POWER_WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        ArraySensorEntityDescription(
            key="ac_output_{}_frequency",
            data_key="ac_output_frequency",
            range=range(3),
            name="AC Output {} - Frequency",
            entity_registry_enabled_default=False,
            icon="mdi:sine-wave",
            native_unit_of_measurement=FREQUENCY_HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
    SERVICE_DEVICE: (
        SensorEntityDescription(
            key="signal_quality",
            name="Signal Quality",
            icon="mdi:wifi",
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        SensorEntityDescription(
            key="ip_address",
            name="IP Address",
            icon="mdi:network",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Omnik Inverter Sensors based on a config entry."""

    def create_sensor_entities(description, service_key):
        if isinstance(description, ArraySensorEntityDescription):
            for i in description.range:
                yield OmnikInverterArraySensorEntity(
                    coordinator=hass.data[DOMAIN][entry.entry_id],
                    index=i,
                    description=description,
                    service_key=service_key,
                    name=entry.title,
                    service=SERVICES[service_key],
                )
        else:
            yield OmnikInverterSensorEntity(
                coordinator=hass.data[DOMAIN][entry.entry_id],
                description=description,
                service_key=service_key,
                name=entry.title,
                service=SERVICES[service_key],
            )

    async_add_entities(
        sensor_entity
        for service_key, service_sensors in SENSORS.items()
        for description in service_sensors
        for sensor_entity in create_sensor_entities(description, service_key)
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


class OmnikInverterArraySensorEntity(OmnikInverterSensorEntity):
    """Defines an Omnik Inverter sensor reading from an array."""

    def __init__(
        self,
        *,
        coordinator: OmnikInverterDataUpdateCoordinator,
        index: int,
        description: ArraySensorEntityDescription,
        service_key: Literal["inverter", "device"],
        name: str,
        service: str,
    ) -> None:
        self.index = index
        self.data_key = description.data_key
        human_index = index + 1

        description = dataclasses.replace(
            description,
            key=description.key.format(human_index),
            name=description.name.format(human_index),
        )

        super().__init__(
            coordinator=coordinator,
            description=description,
            service_key=service_key,
            name=name,
            service=service,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = getattr(self.coordinator.data[self._service_key], self.data_key)
        return value[self.index]
