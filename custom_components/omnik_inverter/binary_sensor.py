"""Support for Omnik Inverter Binary sensors."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SERVICE_DEVICE
from .coordinator import OmnikInverterDataUpdateCoordinator
from .models import OmnikInverterEntity

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Load all Omnik Inverter binary sensors.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.
        async_add_entities: The callback to provide the created entities to.
    """
    coordinator = hass.data[DOMAIN][entry.entry_id]

    """Set up the Goal Zero Yeti sensor."""
    async_add_entities(
        OmnikInverterBinarySensor(
            coordinator,
            name=entry.title,
            description=description,
            service=SERVICE_DEVICE,
        )
        for description in BINARY_SENSORS
    )


class OmnikInverterBinarySensor(OmnikInverterEntity, BinarySensorEntity):
    """Defines an Omnik Inverter Binary Sensor."""

    entity_description: BinarySensorEntityDescription
    _options: dict[Any]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        coordinator: OmnikInverterDataUpdateCoordinator,
        name: str,
        description: BinarySensorEntityDescription,
        service: str,
    ):
        """
        Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            name: The identifier for this entity.
            description: The entity description for the binary sensor.
            service: The service to create the binary sensor for.
            options: The options provided by the user.
        """
        super().__init__(coordinator=coordinator, name=name, service=service)

        self.entity_description = description

        self.entity_id = (
            f"{BINARY_SENSOR_DOMAIN}.{self._name}_{self.entity_description.key}"  # noqa: E501
        )
        self._attr_unique_id = f"{self._name}_{service}_{self.entity_description.key}"
        self._attr_name = self.entity_description.name

    @property
    def is_on(self) -> bool:
        """Return True if the service is on."""
        return self.coordinator.last_update_success
