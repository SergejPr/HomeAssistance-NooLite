import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from custom_components.noolite import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN)
from custom_components.noolite import (NooLiteGenericModule)
from custom_components.noolite import (PLATFORM_SCHEMA)

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=_SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)
    add_devices([NooLiteSwitchDevice(config, hass.data[DOMAIN])])


class NooLiteSwitchDevice(NooLiteGenericModule, SwitchEntity):
    pass
