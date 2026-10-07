"""Omnik Inverter platform configuration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback, valid_entity_id
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import CONFIGFLOW_VERSION, DOMAIN, LOGGER, SERVICE_DEVICE, SERVICE_INVERTER
from .coordinator import OmnikInverterDataUpdateCoordinator

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

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: OmnikInverterConfigEntry
) -> None:
    """Reload the config entry when its data or options change.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry that was updated.

    """
    await hass.config_entries.async_reload(entry.entry_id)


@callback
def _async_set_unique_id(
    hass: HomeAssistant,
    entry: OmnikInverterConfigEntry,
    coordinator: OmnikInverterDataUpdateCoordinator,
) -> None:
    """Set the inverter serial number as unique ID on older config entries.

    Args:
        hass: The HomeAssistant instance.
        entry: The ConfigEntry to update.
        coordinator: The coordinator holding the inverter data.

    """
    serial_number = coordinator.data[SERVICE_INVERTER].serial_number
    if entry.unique_id is not None or not serial_number:
        return
    if hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, serial_number):
        return
    hass.config_entries.async_update_entry(entry, unique_id=serial_number)


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
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Migrate an old entry.

    Args:
        _hass: The HomeAssistant instance.
        config_entry: The ConfigEntry containing the user input.

    Returns:
        Return false, not possible.

    """
    if config_entry.version <= 2:
        LOGGER.warning(
            "Impossible to migrate config version from version %s to version %s."
            "\r\nPlease consider to delete and re-add the integration.",
            config_entry.version,
            CONFIGFLOW_VERSION,
        )
        return False
    return False
