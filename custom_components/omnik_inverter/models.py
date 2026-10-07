"""Support for Omnik Inverter entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.device_registry import ChildDeviceInfo, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, SERVICE_DEVICE, SERVICE_INVERTER, Service
from .coordinator import OmnikInverterDataUpdateCoordinator


def inverter_device_info(coordinator: OmnikInverterDataUpdateCoordinator) -> DeviceInfo:
    """Return the device info of the inverter.

    Args:
        coordinator: The data coordinator holding the inverter data.

    Returns:
        The device info of the inverter.

    """
    entry = coordinator.config_entry
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_{SERVICE_INVERTER}")},
        name=f"{entry.title} Inverter",
        manufacturer=MANUFACTURER,
        # Explicitly clear the service type set by earlier versions.
        entry_type=None,
        model=coordinator.data[SERVICE_INVERTER].model,
        sw_version=coordinator.data[SERVICE_INVERTER].firmware,
        configuration_url=f"http://{coordinator.data[SERVICE_DEVICE].ip_address}",
    )


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
    def device_info(self) -> DeviceInfo | ChildDeviceInfo:
        """Return information to link this entity with the correct device.

        The Wi-Fi module is registered as a child device of the inverter.

        Returns:
            The device info of the inverter or the Wi-Fi module.

        """
        if self.service == SERVICE_INVERTER:
            return inverter_device_info(self.coordinator)
        return ChildDeviceInfo(
            identifiers={(DOMAIN, f"{self.entry_id}_{SERVICE_DEVICE}")},
            parent_device_id=self.coordinator.inverter_device_id,
            translation_key="wifi_module",
        )


@dataclass(frozen=True, kw_only=True)
class RangedSensorEntityDescription(SensorEntityDescription):
    """An extended sensor entity description."""

    size: range | None = None
    data_key: str | None = None
