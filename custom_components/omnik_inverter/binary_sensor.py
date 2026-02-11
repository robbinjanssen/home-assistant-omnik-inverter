"""Support for Omnik Inverter binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import slugify

from .const import SERVICE_DEVICE
from .models import OmnikInverterEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import OmnikInverterConfigEntry
    from .coordinator import OmnikInverterDataUpdateCoordinator

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: OmnikInverterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load all Omnik Inverter binary sensors.

    Args:
        _hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.
        async_add_entities: The callback to provide the created entities to.

    """
    coordinator = entry.runtime_data

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
    _options: dict[str, Any]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        coordinator: OmnikInverterDataUpdateCoordinator,
        name: str,
        description: BinarySensorEntityDescription,
        service: str,
    ) -> None:
        """Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            name: The identifier for this entity.
            description: The entity description for the binary sensor.
            service: The service to create the binary sensor for.

        """
        super().__init__(coordinator=coordinator, name=name, service=service)

        self.entity_description = description

        self._attr_unique_id = slugify(
            f"{self._name}_{service}_{self.entity_description.key}"
        )
        self._attr_name = self.entity_description.name

    @property
    def is_on(self) -> bool:
        """Return True if the service is on.

        Returns:
            True if the device is on.

        """
        return self.coordinator.last_update_success
