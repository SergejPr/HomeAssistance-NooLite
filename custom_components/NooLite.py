"""
Support for NooLite.
"""

import logging

import voluptuous as vol
from homeassistant.components.fan import (SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_RGB_COLOR,
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR)
from homeassistant.const import CONF_NAME, CONF_PORT, CONF_MODE
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['NooLite-F==0.0.19']

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
        responses = DEVICE.on(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST),
                              _module_mode(self._config))
        if self.assumed_state:
            self._state = True
        else:
            self._update_state_from(responses)

    def turn_off(self, **kwargs):
        responses = DEVICE.off(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST),
                               _module_mode(self._config))
        if self.assumed_state:
            self._state = False
        else:
            self._update_state_from(responses)

    def toggle(self, **kwargs) -> None:
        responses = DEVICE.switch(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST),
                                  _module_mode(self._config))
        if self.assumed_state:
            self._state = not self._state
        else:
            self._update_state_from(responses)

    def update(self):
        if not self.assumed_state:
            responses = DEVICE.read_state(None, self._config.get(CONF_CHANNEL), self._config.get(CONF_BROADCAST),
                                          _module_mode(self._config))
            self._update_state_from(responses)

    def _is_module_on(self, module_state) -> bool:
        from NooLite_F import ModuleState
        return module_state.state == ModuleState.ON or module_state.state == ModuleState.TEMPORARY_ON

    def _update_state_from(self, responses):

        state = False
        for (result, info, module_state) in responses:
            if result and module_state is not None:
                state = state or self._is_module_on(module_state)

        self._state = state


class NooLiteDimmerModule(NooLiteModule):
    def __init__(self, hass, config):
        super().__init__(hass, config)
        self._brightness = 255

    @property
    def supported_features(self) -> int:
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        return self._brightness

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        for (result, info, module_state) in responses:
            if result and module_state is not None and super()._is_module_on(module_state):
                self._brightness = module_state.brightness * 255

    def turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is None:
            brightness = self._brightness

        responses = DEVICE.set_brightness(brightness / 255, None, self._config.get(CONF_CHANNEL),
                                          self._config.get(CONF_BROADCAST), _module_mode(self._config))
        if self.assumed_state:
            self._state = True
            self._brightness = brightness
        else:
            self._update_state_from(responses)


class NooLiteFanModule(NooLiteModule):
    def __init__(self, hass, config):
        super().__init__(hass, config)
        self.hass = hass
        self._speed = STATE_OFF

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._speed != STATE_OFF

    @property
    def should_poll(self):
        """No polling needed for a fan."""
        return False

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [STATE_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the entity."""
        if speed is None:
            speed = SPEED_MEDIUM
        self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self.set_speed(STATE_OFF)

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""

        if speed is None:
            speed = self._speed
        int_speed = 0

        if speed == SPEED_HIGH:
            int_speed = 255
        elif speed == SPEED_MEDIUM:
            int_speed = 180
        elif speed == SPEED_LOW:
            int_speed = 70

        responses = DEVICE.set_brightness(int_speed / 255, None, self._config.get(CONF_CHANNEL),
                                          self._config.get(CONF_BROADCAST), _module_mode(self._config))
        if self.assumed_state:
            self._state = True
            self._speed = speed
        else:
            self._update_state_from(responses)

        self.schedule_update_ha_state()

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return 0

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        for (result, info, module_state) in responses:
            if result and module_state is not None and super()._is_module_on(module_state):

                int_speed = int(module_state.brightness * 255)

                self._speed = STATE_OFF

                if 0 < int_speed <= 80:
                    self._speed = SPEED_LOW

                if 80 < int_speed <= 180:
                    self._speed = SPEED_MEDIUM

                if 180 < int_speed:
                    self._speed = SPEED_HIGH


class NooLiteRGBLedModule(NooLiteModule):
    def __init__(self, hass, config):
        super().__init__(hass, config)
        self._brightness = 255
        self._rgb = [255, 255, 255]

    @property
    def supported_features(self) -> int:
        return SUPPORT_COLOR | SUPPORT_BRIGHTNESS

    @property
    def rgb_color(self):
        return self._rgb

    @property
    def brightness(self):
        return self._brightness

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        for (result, info, module_state) in responses:
            if result and module_state is not None and super()._is_module_on(module_state):
                self._brightness = module_state.brightness * 255

    def turn_on(self, **kwargs):
        rgb = kwargs.get(ATTR_RGB_COLOR)
        if rgb is not None:
            self._rgb = rgb

        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is not None:
            self._brightness = brightness

        brightness_multiplier = self._brightness / 255
        red = (self._rgb[0] * brightness_multiplier) / 255
        green = (self._rgb[1] * brightness_multiplier) / 255
        blue = (self._rgb[2] * brightness_multiplier) / 255

        responses = DEVICE.set_rgb_brightness(red, green, blue, None, self._config.get(CONF_CHANNEL),
                                              self._config.get(CONF_BROADCAST), _module_mode(self._config))
        if self.assumed_state:
            self._state = True
        else:
            self._update_state_from(responses)
