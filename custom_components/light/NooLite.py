import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.const import CONF_TYPE, CONF_SCAN_INTERVAL
from homeassistant.components.light import Light

from custom_components.NooLite import PLATFORM_SCHEMA
from custom_components.NooLite import NooLiteModule, NooLiteDimmerModule, NooLiteRGBLedModule
from custom_components.NooLite import CONF_BROADCAST, CONF_CHANNEL


DEPENDENCIES = ['NooLite']


_LOGGER = logging.getLogger(__name__)

TYPES = ['Light', 'Dimmer', 'RGBLed']

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default='Light'): vol.In(TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config.get(CONF_TYPE)

    device = None
    if module_type == 'Dimmer':
        device = NooLiteDimmerSwitch(hass, config)
    elif module_type == 'RGBLed':
        device = NooLiteRGBLedSwitch(hass, config)
    elif module_type == 'Light':
        device = NooLiteSwitch(hass, config)

    if device is not None:
        add_devices([device])


class NooLiteSwitch(NooLiteModule, Light):
    pass


class NooLiteDimmerSwitch(NooLiteDimmerModule, Light):
    pass


class NooLiteRGBLedSwitch(NooLiteRGBLedModule, Light):
    pass
