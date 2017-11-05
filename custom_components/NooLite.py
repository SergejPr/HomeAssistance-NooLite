"""
Support for NooLite.
"""

import logging

import voluptuous as vol

from homeassistant.const import EVENT_HOMEASSISTANT_STOP, CONF_NAME, CONF_PORT, CONF_TYPE
from homeassistant.const import STATE_UNKNOWN

from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv

from NooLite_F import ModuleInfo, ModuleState, ModuleType


REQUIREMENTS = ['NooLite-F==0.0.7']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'NooLite'

CONF_CHANNEL = "channel"
CONF_BROADCAST = "broadcast"

DEFAULT_PORT = '/dev/ttyUSB0'

DEVICE = None


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_TYPE): cv.string,
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the connection to the ZigBee device."""
    global DEVICE

    from NooLite_F.MTRF64 import MTRF64Controller
    from serial import SerialException

    try:
        DEVICE = MTRF64Controller(config[DOMAIN].get(CONF_PORT))
    except SerialException as exc:
        _LOGGER.exception("Unable to open serial port for NooLite: %s", exc)
        return False

    return True


class NooLiteModule(Entity):

    def __init__(self, hass, config):
        self._config = config
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        return self._config.get(CONF_NAME)

    @property
    def config(self):
        return self._config

    @property
    def is_on(self):
        return self._state

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return self._module_type() == ModuleType.NOOLITE

    def turn_on(self, **kwargs):
        responses = DEVICE.on(self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), self._module_type())
        self._update_state_from(responses)

    def turn_off(self, **kwargs):
        responses = DEVICE.off(self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), self._module_type())
        self._update_state_from(responses)

    def toggle(self, **kwargs) -> None:
        responses = DEVICE.switch(self._config.channel, self._config.broadcast)
        self._update_state_from(responses)

    def update(self):
        responses = DEVICE.read_state(self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), self._module_type())
        self._update_state_from(responses)

    def _update_state_from(self, responses):
        state = False
        for (result, info) in responses:
            if result and info is not None and (info.state == ModuleState.ON or info.state == ModuleState.TEMPORARY_ON):
                state = True

        self._state = state

    def _module_type(self) -> ModuleType:
        type = self._config.get(CONF_TYPE)

        if type == 'NooLite':
            device_type = ModuleType.NOOLITE
        else:
            device_type = ModuleType.NOOLITE_F

        return device_type
