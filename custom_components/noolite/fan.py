import logging

import voluptuous as vol
from NooLite_F import Direction
from homeassistant.components.fan import (FanEntity, FanEntityFeature, PLATFORM_SCHEMA)
from homeassistant.const import CONF_NAME, CONF_MODE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv, entity_platform

from .base import (NooLiteGenericModule, should_pull_on_start)
from .const import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN, CONF_SPEED_ENABLED,
                    SCAN_INTERVAL, CONF_SPEED_COUNT, LOG_LEVEL, DEVICE_CLASS_FAN, TUNE_SCHEMA, TUNE_DIRECTION_FIELD,
                    TUNE_DIRECTION_UP, TUNE_DIRECTION_DOWN, TUNE_DIRECTION_REVERSE)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(LOG_LEVEL)

SERVICE_FAN_START_SPEED_TUNE = 'fan_start_speed_tune'
SERVICE_FAN_STOP_SPEED_TUNE = 'fan_stop_speed_tune'
SERVICE_FAN_LOAD_PRESET = 'fan_load_preset'
SERVICE_FAN_SAVE_PRESET = 'fan_save_preset'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Optional(CONF_SPEED_ENABLED, default=False): cv.boolean,
    vol.Optional(CONF_SPEED_COUNT, default=100): cv.positive_int,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info(config)
    add_devices([NooLiteFan(config, hass.data[DOMAIN])], should_pull_on_start(config))

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SERVICE_FAN_START_SPEED_TUNE, TUNE_SCHEMA, _start_speed_tune)
    platform.async_register_entity_service(SERVICE_FAN_STOP_SPEED_TUNE, {}, _stop_speed_tune)
    platform.async_register_entity_service(SERVICE_FAN_LOAD_PRESET, {}, _load_preset)
    platform.async_register_entity_service(SERVICE_FAN_SAVE_PRESET, {}, _save_preset)


def _start_speed_tune(entity, service_call):
    if hasattr(entity, "start_speed_tune"):
        entity.start_speed_tune(service_call.data[TUNE_DIRECTION_FIELD])
    else:
        _LOGGER.error("{0} doesn't support start_speed_tune command".format(entity.name))


def _stop_speed_tune(entity, service_call):
    if hasattr(entity, "stop_speed_tune"):
        entity.stop_speed_tune()
    else:
        _LOGGER.error("{0} doesn't support stop_speed_tune command".format(entity.name))


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


class NooLiteFan(NooLiteGenericModule, FanEntity):

    def __init__(self, config, device):
        super().__init__(config, device)
        self._last_turn_on_percentage = 100
        if config[CONF_SPEED_ENABLED] is True:
            self._attr_speed_count = config[CONF_SPEED_COUNT]
            self._attr_supported_features = FanEntityFeature(FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF)
            self._attr_device_class = DEVICE_CLASS_FAN

    def turn_on(self, percentage: int = None, preset_mode: str = None, **kwargs) -> None:
        if percentage is None:
            percentage = self._last_turn_on_percentage

        if percentage > 0:
            self._last_turn_on_percentage = percentage

        responses = self._device.set_brightness(percentage / 100, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_percentage = percentage
        else:
            self._update_state_from(responses)

    def turn_off(self, **kwargs):
        responses = self._device.off(None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_percentage = 0
        else:
            self._update_state_from(responses)

    def set_percentage(self, percentage: int) -> None:
        self.turn_on(percentage=percentage)

    def _update_state_from(self, responses, ignore_next=True):
        super()._update_state_from(responses, ignore_next)
        self._attr_percentage = self._level * 100

    def set_direction(self, direction: str) -> None:
        pass

    def set_preset_mode(self, preset_mode: str) -> None:
        self.turn_on(preset_mode=preset_mode)

    def oscillate(self, oscillating: bool) -> None:
        pass

    def start_speed_tune(self, direction: str):
        if direction == TUNE_DIRECTION_UP:
            self._device.brightness_tune(Direction.UP, None, self._channel, self._broadcast, self._mode)
        elif direction == TUNE_DIRECTION_DOWN:
            self._device.brightness_tune(Direction.DOWN, None, self._channel, self._broadcast, self._mode)
        elif direction == TUNE_DIRECTION_REVERSE:
            self._device.brightness_tune_back(None, self._channel, self._broadcast, self._mode)
        else:
            _LOGGER.warning("Unknown direction: {0}".format(direction))

    def stop_speed_tune(self):
        self._device.brightness_tune_stop(None, self._channel, self._broadcast, self._mode)
