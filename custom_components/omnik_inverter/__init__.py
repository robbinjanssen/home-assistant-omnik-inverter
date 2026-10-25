"""Omnik Inverter platform configuration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback, valid_entity_id
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import (
    CONF_SOURCE_TYPE,
    CONFIGFLOW_MINOR_VERSION,
    DOMAIN,
    LOGGER,
    SERVICE_DEVICE,
    SERVICE_INVERTER,
)
from .coordinator import OmnikInverterDataUpdateCoordinator
from .models import config_entry_unique_id, inverter_device_info

type OmnikInverterConfigEntry = ConfigEntry[OmnikInverterDataUpdateCoordinator]

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> bool:
    """Set up OmnikInverter as config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true after setting up.

    """
    await _async_migrate_entities(hass, entry)

    coordinator = OmnikInverterDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    _async_set_unique_id(hass, entry, coordinator)

    # Register the inverter first, the Wi-Fi module is added as its child device.
    inverter_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, **inverter_device_info(coordinator)
    )
    coordinator.inverter_device_id = inverter_device.id

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


@callback
def _async_set_unique_id(
    hass: HomeAssistant,
    entry: OmnikInverterConfigEntry,
    coordinator: OmnikInverterDataUpdateCoordinator,
) -> None:
    """Set the inverter serial number and source type as unique ID on older entries.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry to update.
        coordinator: The coordinator holding the inverter data.

    """
    serial_number = coordinator.data[SERVICE_INVERTER].serial_number
    if entry.unique_id is not None or not serial_number:
        return
    unique_id = config_entry_unique_id(serial_number, entry.data[CONF_SOURCE_TYPE])
    if hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, unique_id):
        return
    hass.config_entries.async_update_entry(entry, unique_id=unique_id)


async def _async_migrate_entities(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> None:
    """Migrate entity registry entries created by older versions.

    Version 2.x used unique IDs that were not slugified and could set
    entity IDs containing capitals or spaces. Up to version 3.0.0 the
    binary sensor unique ID was based on the entry title instead of the
    entry ID. Rewrite those entries so existing entities, including their
    history, are kept after updating.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry to migrate the entities for.

    """
    ent_reg = er.async_get(hass)

    @callback
    def _migrate(entity_entry: er.RegistryEntry) -> dict[str, str] | None:
        updates: dict[str, str] = {}

        new_unique_id = slugify(entity_entry.unique_id)
        if entity_entry.domain == Platform.BINARY_SENSOR:
            key = new_unique_id.rsplit(f"_{SERVICE_DEVICE}_", 1)[-1]
            new_unique_id = slugify(f"{entry.entry_id}_{SERVICE_DEVICE}_{key}")
        if new_unique_id != entity_entry.unique_id:
            if ent_reg.async_get_entity_id(entity_entry.domain, DOMAIN, new_unique_id):
                LOGGER.warning(
                    "Cannot migrate %s to unique ID %s, it is already in use",
                    entity_entry.entity_id,
                    new_unique_id,
                )
                return None
            updates["new_unique_id"] = new_unique_id

        if not valid_entity_id(entity_entry.entity_id):
            object_id = entity_entry.entity_id.split(".", 1)[1]
            new_entity_id = f"{entity_entry.domain}.{slugify(object_id)}"
            if not ent_reg.async_is_registered(new_entity_id):
                updates["new_entity_id"] = new_entity_id

        return updates or None

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)


async def async_unload_entry(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> bool:
    """Unload a config entry.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry containing the user input.

    Returns:
        Return true if unload was successful, false otherwise.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Migrate an old entry.

    Version 2.1 used the serial number as unique ID, which allowed only
    one entry per inverter. Version 2.2 adds the source type to it.

    Args:
        hass: The HomeAssistant instance.
        config_entry: The ConfigEntry containing the user input.

    Returns:
        Return true after migrating.

    Raises:
        ConfigEntryError: Entries of version 1 cannot be migrated.

    """
    if config_entry.version == 2 and config_entry.minor_version < 2:
        unique_id = config_entry.unique_id
        if unique_id is not None:
            unique_id = config_entry_unique_id(
                unique_id, config_entry.data[CONF_SOURCE_TYPE]
            )
        hass.config_entries.async_update_entry(
            config_entry,
            unique_id=unique_id,
            minor_version=CONFIGFLOW_MINOR_VERSION,
        )
        return True

    LOGGER.debug("Cannot migrate config entry version %s", config_entry.version)
    raise ConfigEntryError(
        translation_domain=DOMAIN,
        translation_key="migration_not_supported",
        translation_placeholders={"version": str(config_entry.version)},
    )
