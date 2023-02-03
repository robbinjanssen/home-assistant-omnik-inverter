"""Support for Omnik Inverter entities."""
from __future__ import annotations
from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, SERVICE_DEVICE, SERVICE_INVERTER
from .coordinator import OmnikInverterDataUpdateCoordinator


class OmnikInverterEntity(CoordinatorEntity[OmnikInverterDataUpdateCoordinator], Entity):
    """Defines an Omnik Inverter Entity."""

    idx: str
    coordinator: OmnikInverterDataUpdateCoordinator
    service: str

    def __init__(
        self, 
        coordinator: OmnikInverterDataUpdateCoordinator, 
        idx: str,
        service: str,
    ) -> None:
        """
        Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            idx: The identifier for this entity.
        """
        super().__init__(coordinator)
        self.idx = idx
        self.coordinator = coordinator
        self.service = service

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return information to link this entity with the correct device.

        Returns:
            The device identifiers to make sure the entity is attached
            to the correct device.
        """
        return DeviceInfo(
            identifiers={
                (DOMAIN, f"{self.idx}_{self.service}")
            },
            name=self.service,
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
            model= self.coordinator.data[SERVICE_INVERTER].model,
            sw_version=self.coordinator.data[self.service].firmware,
            configuration_url=f'http://{ self.coordinator.data[SERVICE_DEVICE].ip_address}',
        )


@dataclass
class RangedSensorEntityDescription(SensorEntityDescription):
    range: range | None = None
    data_key: str | None = None
