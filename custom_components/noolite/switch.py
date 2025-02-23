import logging

import voluptuous as vol
from homeassistant.components.switch import (SwitchEntity, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_MODE, CONF_SCAN_INTERVAL)
from homeassistant.helpers import config_validation as cv, entity_platform

from .base import (NooLiteGenericModule, should_pull_on_start)
from .const import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN, SCAN_INTERVAL, LOG_LEVEL,
                    DEVICE_CLASS_SWITCH)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(LOG_LEVEL)

SERVICE_SWITCH_LOAD_PRESET = 'switch_load_preset'
SERVICE_SWITCH_SAVE_PRESET = 'switch_save_preset'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)
    add_devices([NooLiteSwitchDevice(config, hass.data[DOMAIN])], should_pull_on_start(config))

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SERVICE_SWITCH_LOAD_PRESET, {}, _load_preset)
    platform.async_register_entity_service(SERVICE_SWITCH_SAVE_PRESET, {}, _save_preset)


def _load_preset(entity, service_call):
    if hasattr(entity, "load_preset"):
        entity.load_preset()
    else:
        _LOGGER.error("{0} doesn't support load_preset command".format(entity.name))


def _save_preset(entity, service_call):
    if hasattr(entity, "save_preset"):
        entity.save_preset()
    else:
        _LOGGER.error("{0} doesn't support save_preset command".format(entity.name))


class NooLiteSwitchDevice(NooLiteGenericModule, SwitchEntity):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_device_class = DEVICE_CLASS_SWITCH
