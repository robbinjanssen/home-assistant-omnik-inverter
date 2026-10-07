"""Support for Omnik Inverter entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, SERVICE_DEVICE, SERVICE_INVERTER, Service
from .coordinator import OmnikInverterDataUpdateCoordinator


class OmnikInverterEntity(CoordinatorEntity[OmnikInverterDataUpdateCoordinator]):
    """Defines an Omnik Inverter Entity."""

    _attr_has_entity_name = True
    _name: str
    coordinator: OmnikInverterDataUpdateCoordinator
    service: Service
    entry_id: str

    def __init__(
        self,
        coordinator: OmnikInverterDataUpdateCoordinator,
        name: str,
        service: Service,
    ) -> None:
        """Initialise the entity.

        Args:
            coordinator: The data coordinator updating the models.
            name: The identifier for this entity.
            service: The service (Device or Inverter)/

        """
        super().__init__(coordinator)
        self._name = name
        self.coordinator = coordinator
        self.service = service
        self.entry_id = coordinator.config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return information to link this entity with the correct device.

        Returns:
            The device identifiers to make sure the entity is attached
            to the correct device.

        """
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.entry_id}_{self.service}")},
            name=f"{self._name} {self.service.title()}",
            manufacturer=MANUFACTURER,
            # Explicitly clear the service type set by earlier versions.
            entry_type=None,
            model=self.coordinator.data[SERVICE_INVERTER].model,
            sw_version=self.coordinator.data[self.service].firmware,
            configuration_url=f"http://{self.coordinator.data[SERVICE_DEVICE].ip_address}",
        )


@dataclass(frozen=True, kw_only=True)
class RangedSensorEntityDescription(SensorEntityDescription):
    """An extended sensor entity description."""

    size: range | None = None
    data_key: str | None = None
