"""Support for Omnik Inverter Aqara sensors."""
from __future__ import annotations

import dataclasses
from typing import Any, Literal

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SERVICE_DEVICE, SERVICE_INVERTER
from .coordinator import OmnikInverterDataUpdateCoordinator
from .models import OmnikInverterEntity, RangedSensorEntityDescription

SENSORS: dict[Literal["inverter", "device"], tuple[SensorEntityDescription, ...]] = {
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
    SERVICE_INVERTER: (
        SensorEntityDescription(
            key="solar_current_power",
            name="Current Power Production",
            icon="mdi:weather-sunny",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        SensorEntityDescription(
            key="solar_energy_today",
            name="Solar Production - Today",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_energy_total",
            name="Solar Production - Total",
            icon="mdi:chart-line",
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="solar_hours_total",
            name="Solar Production - Uptime",
            icon="mdi:clock",
            native_unit_of_measurement=UnitOfTime.HOURS,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        SensorEntityDescription(
            key="temperature",
            name="Inverter temperature",
            entity_registry_enabled_default=False,
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="dc_input_{}_voltage",
            size=range(3),
            data_key="dc_input_voltage",
            name="DC Input {} - Voltage",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="dc_input_{}_current",
            size=range(3),
            data_key="dc_input_current",
            name="DC Input {} - Current",
            entity_registry_enabled_default=False,
            icon="mdi:current-dc",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="ac_output_{}_voltage",
            size=range(3),
            data_key="ac_output_voltage",
            name="AC Output {} - Voltage",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="ac_output_{}_current",
            size=range(3),
            data_key="ac_output_current",
            name="AC Output {} - Current",
            entity_registry_enabled_default=False,
            icon="mdi:current-ac",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="ac_output_{}_power",
            size=range(3),
            data_key="ac_output_power",
            name="AC Output {} - Power",
            entity_registry_enabled_default=False,
            icon="mdi:lightning-bolt",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        RangedSensorEntityDescription(  # pylint: disable=unexpected-keyword-arg
            key="ac_output_{}_frequency",
            size=range(3),
            data_key="ac_output_frequency",
            name="AC Output {} - Frequency",
            entity_registry_enabled_default=False,
            icon="mdi:sine-wave",
            native_unit_of_measurement=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Load all Omnik Inverter sensors.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.
        async_add_entities: The callback to provide the created entities to.
    """
    coordinator = hass.data[DOMAIN][entry.entry_id]
    options = entry.options

    def create_sensor_entities(description, service):
        if isinstance(description, RangedSensorEntityDescription):
            for i in description.size:
                yield OmnikInverterRangedSensor(
                    coordinator=coordinator,
                    index=i,
                    name=entry.title,
                    description=description,
                    service=service,
                    options=options,
                )
        else:
            yield OmnikInverterSensor(
                coordinator=coordinator,
                name=entry.title,
                description=description,
                service=service,
                options=options,
            )

    entities = (
        sensor_entity
        for service, service_sensors in SENSORS.items()
        for description in service_sensors
        for sensor_entity in create_sensor_entities(description, service)
    )

    async_add_entities(entities)


class OmnikInverterSensor(OmnikInverterEntity, SensorEntity):
    """Defines an Omnik Inverter Sensor."""

    entity_description: SensorEntityDescription
    _options: dict[Any]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        coordinator: OmnikInverterDataUpdateCoordinator,
        name: str,
        description: SensorEntityDescription,
        service: str,
        options: dict[Any],
    ):
        """
        Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            name: The identifier for this entity.
            description: The entity description for the sensor.
            service: The service to create the sensor for.
            options: The options provided by the user.
        """
        super().__init__(coordinator=coordinator, name=name, service=service)

        self.entity_description = description
        self._options = options

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{self._name}_{self.entity_description.key}"  # noqa: E501
        )
        self._attr_unique_id = f"{self._name}_{service}_{self.entity_description.key}"
        self._attr_name = self.entity_description.name

    @property
    def native_value(self) -> Any | None:
        """
        Return the state of the sensor.

        Returns:
            The current state value of the sensor.
        """
        value = getattr(
            self.coordinator.data[self.service], self.entity_description.key
        )

        if isinstance(value, str):
            return value.lower()

        return value


class OmnikInverterRangedSensor(OmnikInverterSensor):
    """Defines an Omnik Inverter Sensor."""

    _index: int
    _data_key: str

    def __init__(  # pylint: disable=too-many-arguments
        self,
        coordinator: OmnikInverterDataUpdateCoordinator,
        index: int,
        name: str,
        description: RangedSensorEntityDescription,
        service: str,
        options: dict[Any],
    ):
        """
        Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            index: The index for the ranged sensor.
            name: The identifier for this entity.
            description: The entity description for the sensor.
            service: The service to create the sensor for.
            options: The options provided by the user.
        """
        self._index = index
        self._data_key = description.data_key
        description = dataclasses.replace(
            description,
            key=description.key.format(index + 1),
            name=description.name.format(index + 1),
        )

        super().__init__(
            coordinator=coordinator,
            name=name,
            description=description,
            service=service,
            options=options,
        )

    @property
    def native_value(self) -> Any | None:
        """
        Return the state of the sensor.

        Returns:
            The current state value of the sensor.
        """
        value = getattr(self.coordinator.data[self.service], self._data_key)

        if value is not None:
            return value[self._index]

        return None
