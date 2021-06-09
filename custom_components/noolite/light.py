import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.light import LightEntity, SUPPORT_BRIGHTNESS, ATTR_BRIGHTNESS, SUPPORT_COLOR, ATTR_RGB_COLOR
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.const import CONF_TYPE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from custom_components.noolite import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN)
from custom_components.noolite import (NooLiteGenericModule)
from custom_components.noolite import (PLATFORM_SCHEMA)

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_SCAN_INTERVAL = timedelta(seconds=60)

_TYPE_LIGHT = 'light'
_TYPE_DIMMER = 'dimmer'
_TYPE_RGB_LED = 'rgb_led'

_TYPES = [_TYPE_LIGHT, _TYPE_DIMMER, _TYPE_RGB_LED]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default=_TYPE_LIGHT): vol.In(_TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=_SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == _TYPE_LIGHT:
        devices.append(NooLiteSwitch(config, hass.data[DOMAIN]))
    elif module_type == _TYPE_DIMMER:
        devices.append(NooLiteDimmerSwitch(config, hass.data[DOMAIN]))
    elif module_type == _TYPE_RGB_LED:
        devices.append(NooLiteRGBLedSwitch(config, hass.data[DOMAIN]))

    add_devices(devices)


class NooLiteSwitch(NooLiteGenericModule, LightEntity):
    pass


class NooLiteDimmerSwitch(NooLiteSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._brightness = 255

    @property
    def supported_features(self) -> int:
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        return self._brightness

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        if self.is_on:
            self._brightness = self._level * 255

    def turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is None:
            brightness = self._brightness

        responses = self._device.set_brightness(brightness / 255, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._state = True
            self._brightness = brightness
        else:
            self._update_state_from(responses)


class NooLiteRGBLedSwitch(NooLiteDimmerSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._rgb = [255, 255, 255]

    @property
    def supported_features(self) -> int:
        return SUPPORT_COLOR | SUPPORT_BRIGHTNESS

    @property
    def rgb_color(self):
        return self._rgb

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

        responses = self._device.set_rgb_brightness(red, green, blue, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._state = True
            self._brightness = brightness
            self._rgb = rgb
        else:
            self._update_state_from(responses)
