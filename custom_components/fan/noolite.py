"""
Fan platform for NooLite

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.fan import (FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION)
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.const import CONF_TYPE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from custom_components.noolite import CONF_BROADCAST, CONF_CHANNEL
from custom_components.noolite import NooLiteFanModule
from custom_components.noolite import PLATFORM_SCHEMA

FULL_SUPPORT = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
LIMITED_SUPPORT = SUPPORT_SET_SPEED

DEPENDENCIES = ['NooLite']

TYPES = ['Fan']

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default='Fan'): vol.In(TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info(config)

    module_type = config.get(CONF_TYPE)

    device = None
    if module_type == 'Fan':
        device = NooLiteFan(hass, config)

    if device is not None:
        add_devices([device])


class NooLiteFan(NooLiteFanModule, FanEntity):
    pass
