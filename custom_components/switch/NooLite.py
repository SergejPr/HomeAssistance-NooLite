import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_TYPE
from homeassistant.components.switch import SwitchDevice

from custom_components.NooLite import PLATFORM_SCHEMA
from custom_components.NooLite import NooLiteModule
from custom_components.NooLite import CONF_BROADCAST, CONF_CHANNEL
from homeassistant.const import CONF_NAME, CONF_MODE


DEPENDENCIES = ['NooLite']


_LOGGER = logging.getLogger(__name__)

TYPES = ['Switch']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default='Switch'): vol.In(TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config.get(CONF_TYPE)

    device = None
    if module_type == 'Switch':
        device = NooLiteSwitchDevice(hass, config)

    if device is not None:
        add_devices([device])


class NooLiteSwitchDevice(NooLiteModule, SwitchDevice):
    pass
