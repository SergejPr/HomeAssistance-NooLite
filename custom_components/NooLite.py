"""
Support for NooLite.
"""

import logging
import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_PORT, CONF_MODE
from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv

REQUIREMENTS = ['NooLite-F==0.0.15']

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
    vol.Required(CONF_MODE): cv.string,
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

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, _release_noolite)

    return True


def _release_noolite(*args):
    DEVICE.release()


def _module_mode(config):
    from NooLite_F import ModuleMode

    mode = config.get(CONF_MODE)

    if mode == 'NooLite':
        module_mode = ModuleMode.NOOLITE
    else:
        module_mode = ModuleMode.NOOLITE_F

    return module_mode


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
        from NooLite_F import ModuleMode
        return _module_mode(self._config) == ModuleMode.NOOLITE

    def turn_on(self, **kwargs):
        responses = DEVICE.on(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))
        self._update_state_from(responses)

    def turn_off(self, **kwargs):
        responses = DEVICE.off(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))
        self._update_state_from(responses)

    def toggle(self, **kwargs) -> None:
        responses = DEVICE.switch(None, self._config.channel, self._config.broadcast)
        self._update_state_from(responses)

    def update(self):
        responses = DEVICE.read_state(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))
        self._update_state_from(responses)

    def _update_state_from(self, responses):
        from NooLite_F import ModuleState

        state = False
        for (result, info) in responses:
            if result and info is not None:
                if info.state == ModuleState.ON or info.state == ModuleState.TEMPORARY_ON:
                    state = True

        self._state = state


class NooLiteDimmerModule(NooLiteModule):

    def __init__(self, hass, config):
        super().__init__(hass, config)
        self._brightness = None

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        DEVICE.set_brightness(brightness, None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))

    def _update_state_from(self, responses):
        super()._update_state_from(responses)

        for (result, info) in responses:
            if result and info is not None:
                self._brightness = info.brightness


class NooLiteRGBLedModule(NooLiteModule):

    def __init__(self, hass, config):
        super().__init__(hass, config)
        self._rgb = None
        self._brightness = None

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        DEVICE.set_brightness(brightness, None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))

    @property
    def rgb_color(self):
        """Return the RGB color value [int, int, int]."""
        return self._rgb

    @rgb_color.setter
    def rgb_color(self, rgb):
        DEVICE.set_rgb_brightness(rgb[0], rgb[1], rgb[2], None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST), _module_mode(self._config))

    def _update_state_from(self, responses):
        super()._update_state_from(responses)

        for (result, info) in responses:
            if result and info is not None:
                self._brightness = info.brightness

