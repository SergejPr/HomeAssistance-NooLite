import logging

import voluptuous as vol
from homeassistant.components.light import (LightEntity, COLOR_MODE_BRIGHTNESS, ATTR_BRIGHTNESS, COLOR_MODE_RGB,
                                            ATTR_RGB_COLOR)
from homeassistant.const import (CONF_NAME, CONF_MODE, CONF_TYPE, CONF_SCAN_INTERVAL)
from homeassistant.helpers import config_validation as cv

from . import (PLATFORM_SCHEMA)
from .base import (NooLiteGenericModule, should_pull_on_start)
from .const import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN, SCAN_INTERVAL,
                    TYPE_LIGHT, TYPE_DIMMER, TYPE_RGB_LED, LOG_LEVEL)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(LOG_LEVEL)

_TYPES = [TYPE_LIGHT, TYPE_DIMMER, TYPE_RGB_LED]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default=TYPE_LIGHT): vol.In(_TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == TYPE_LIGHT:
        devices.append(NooLiteSwitch(config, hass.data[DOMAIN]))
    elif module_type == TYPE_DIMMER:
        devices.append(NooLiteDimmerSwitch(config, hass.data[DOMAIN]))
    elif module_type == TYPE_RGB_LED:
        devices.append(NooLiteRGBLedSwitch(config, hass.data[DOMAIN]))

    add_devices(devices, should_pull_on_start(config))


class NooLiteSwitch(NooLiteGenericModule, LightEntity):
    pass


class NooLiteDimmerSwitch(NooLiteSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_brightness = 255
        self._attr_supported_color_modes = {COLOR_MODE_BRIGHTNESS}

    def _update_state_from(self, responses, ignore_next=True):
        super()._update_state_from(responses, ignore_next)
        if self.is_on:
            self._attr_brightness = self._level * 255

    def turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is None:
            brightness = self.brightness

        responses = self._device.set_brightness(brightness / 255, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_is_on = True
            self._attr_brightness = brightness
        else:
            self._update_state_from(responses)


class NooLiteRGBLedSwitch(NooLiteDimmerSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_rgb_color = (255, 255, 255)
        self._attr_supported_color_modes = {COLOR_MODE_BRIGHTNESS, COLOR_MODE_RGB}

    def turn_on(self, **kwargs):
        rgb = kwargs.get(ATTR_RGB_COLOR)
        if rgb is None:
            rgb = self.rgb_color

        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is None:
            brightness = self.brightness

        brightness_multiplier = brightness / 255
        red = (rgb[0] * brightness_multiplier) / 255
        green = (rgb[1] * brightness_multiplier) / 255
        blue = (rgb[2] * brightness_multiplier) / 255

        responses = self._device.set_rgb_brightness(red, green, blue, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_is_on = True
            self._attr_brightness = brightness
            self._attr_rgb_color = rgb
        else:
            self._update_state_from(responses)
