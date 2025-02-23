import logging

import voluptuous as vol
from NooLite_F import Direction
from homeassistant.components.light import (LightEntity, ColorMode, ATTR_BRIGHTNESS,
                                            ATTR_RGB_COLOR, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_MODE, CONF_TYPE, CONF_SCAN_INTERVAL)
from homeassistant.helpers import config_validation as cv, entity_platform

from .base import (NooLiteGenericModule, should_pull_on_start)
from .const import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN, SCAN_INTERVAL,
                    TYPE_LIGHT, TYPE_DIMMER, TYPE_RGB_LED, LOG_LEVEL,
                    DEVICE_CLASS_DIMMER, DEVICE_CLASS_RGB, TUNE_DIRECTION_UP, TUNE_DIRECTION_DOWN,
                    TUNE_DIRECTION_REVERSE, TUNE_SCHEMA, TUNE_DIRECTION_FIELD)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(LOG_LEVEL)

_TYPES = [TYPE_LIGHT, TYPE_DIMMER, TYPE_RGB_LED]

SERVICE_LIGHT_START_BRIGHTNESS_TUNE = 'light_start_brightness_tune'
SERVICE_LIGHT_STOP_BRIGHTNESS_TUNE = 'light_stop_brightness_tune'
SERVICE_LIGHT_LOAD_PRESET = 'light_load_preset'
SERVICE_LIGHT_SAVE_PRESET = 'light_save_preset'

SERVICE_RGB_START_BRIGHTNESS_TUNE = 'rgb_start_brightness_tune'
SERVICE_RGB_STOP_TUNE = 'rgb_stop_tune'
SERVICE_RGB_START_ROLL_COLOR = 'rgb_start_roll_color'
SERVICE_RGB_SWITCH_COLOR = 'rgb_switch_color'
SERVICE_RGB_SWITCH_MODE = 'rgb_switch_mode'
SERVICE_RGB_START_SWITCH_SPEED = 'rgb_start_switch_speed'
SERVICE_RGB_LOAD_PRESET = 'rgb_load_preset'
SERVICE_RGB_SAVE_PRESET = 'rgb_save_preset'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default=TYPE_LIGHT): vol.In(_TYPES),
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
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

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SERVICE_LIGHT_START_BRIGHTNESS_TUNE, TUNE_SCHEMA, _start_brightness_tune)
    platform.async_register_entity_service(SERVICE_LIGHT_STOP_BRIGHTNESS_TUNE, {}, _stop_tune)
    platform.async_register_entity_service(SERVICE_LIGHT_LOAD_PRESET, {}, _load_preset)
    platform.async_register_entity_service(SERVICE_LIGHT_SAVE_PRESET, {}, _save_preset)

    platform.async_register_entity_service(SERVICE_RGB_START_BRIGHTNESS_TUNE, TUNE_SCHEMA, _start_brightness_tune)
    platform.async_register_entity_service(SERVICE_RGB_START_ROLL_COLOR, {}, _start_roll_color)
    platform.async_register_entity_service(SERVICE_RGB_SWITCH_COLOR, {}, _switch_color)
    platform.async_register_entity_service(SERVICE_RGB_SWITCH_MODE, {}, _switch_mode)
    platform.async_register_entity_service(SERVICE_RGB_START_SWITCH_SPEED, {}, _start_switch_speed)
    platform.async_register_entity_service(SERVICE_RGB_STOP_TUNE, {}, _stop_tune)
    platform.async_register_entity_service(SERVICE_RGB_LOAD_PRESET, {}, _load_preset)
    platform.async_register_entity_service(SERVICE_RGB_SAVE_PRESET, {}, _save_preset)


def _start_brightness_tune(entity, service_call):
    if hasattr(entity, "start_brightness_tune"):
        entity.start_brightness_tune(service_call.data[TUNE_DIRECTION_FIELD])
    else:
        _LOGGER.error("{0} doesn't support start_brightness_tune command".format(entity.name))


def _stop_tune(entity, service_call):
    if hasattr(entity, "stop_tune"):
        entity.stop_tune()
    else:
        _LOGGER.error("{0} doesn't support stop_tune command".format(entity.name))


def _start_roll_color(entity, service_call):
    if hasattr(entity, "start_roll_color"):
        entity.start_roll_color()
    else:
        _LOGGER.error("{0} doesn't support start_roll_color command".format(entity.name))


def _switch_color(entity, service_call):
    if hasattr(entity, "switch_color"):
        entity.switch_color()
    else:
        _LOGGER.error("{0} doesn't support switch_color command".format(entity.name))


def _switch_mode(entity, service_call):
    if hasattr(entity, "switch_mode"):
        entity.switch_mode()
    else:
        _LOGGER.error("{0} doesn't support switch_mode command".format(entity.name))


def _start_switch_speed(entity, service_call):
    if hasattr(entity, "start_switch_speed"):
        entity.start_switch_speed()
    else:
        _LOGGER.error("{0} doesn't support start_switch_speed command".format(entity.name))


def _load_preset(entity, service_call):
    if hasattr(entity, "load_preset"):
        entity.load_preset()
    else:
        _LOGGER.error("{0} doesn't support load_preset command".format(entity.name))


def _save_preset(entity, service_call):
    if hasattr(entity, "save_preset"):
        entity.save_preset()
    else:
        _LOGGER.error("{0} doesn't support save_preset command".format(entity.name))


class NooLiteSwitch(NooLiteGenericModule, LightEntity):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF


class NooLiteDimmerSwitch(NooLiteSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_brightness = 255
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_device_class = DEVICE_CLASS_DIMMER

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

    def start_brightness_tune(self, direction: str):
        if direction == TUNE_DIRECTION_UP:
            self._device.brightness_tune(Direction.UP, None, self._channel, self._broadcast, self._mode)
        elif direction == TUNE_DIRECTION_DOWN:
            self._device.brightness_tune(Direction.DOWN, None, self._channel, self._broadcast, self._mode)
        elif direction == TUNE_DIRECTION_REVERSE:
            self._device.brightness_tune_back(None, self._channel, self._broadcast, self._mode)
        else:
            _LOGGER.warning("Unknown direction: {0}".format(direction))

    def stop_tune(self):
        self._device.brightness_tune_stop(None, self._channel, self._broadcast, self._mode)


class NooLiteRGBLedSwitch(NooLiteDimmerSwitch):
    def __init__(self, config, device):
        super().__init__(config, device)
        self._attr_rgb_color = (255, 255, 255)
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_device_class = DEVICE_CLASS_RGB

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

    def start_roll_color(self):
        self._device.roll_rgb_color(None, self._channel, self._broadcast, self._mode)

    def switch_color(self):
        self._device.switch_rgb_color(None, self._channel, self._broadcast, self._mode)

    def switch_mode(self):
        self._device.switch_rgb_mode(None, self._channel, self._broadcast, self._mode)

    def start_switch_speed(self):
        self._device.switch_rgb_mode_speed(None, self._channel, self._broadcast, self._mode)
