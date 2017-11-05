import logging

from homeassistant.components.light import Light
from custom_components.NooLite import NooLiteModule


DEPENDENCIES = ['NooLite']

_LOGGER = logging.getLogger(__name__)

CONF_MODULE = 'module'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)
    add_devices([NooLiteSwitch(hass, config)])


class NooLiteSwitch(NooLiteModule, Light):
    pass
