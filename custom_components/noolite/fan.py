import logging

import voluptuous as vol
from homeassistant.components.fan import (FanEntity, SUPPORT_SET_SPEED)
from homeassistant.const import CONF_NAME, CONF_MODE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from . import (PLATFORM_SCHEMA)
from .base import (NooLiteGenericModule)
from .const import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, DOMAIN, CONF_SPEED_ENABLED,
                    SCAN_INTERVAL, CONF_SPEED_COUNT)

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Optional(CONF_SPEED_ENABLED, default=False): cv.boolean,
    vol.Optional(CONF_SPEED_COUNT, default=100): cv.positive_int,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info(config)
    add_devices([NooLiteFan(config, hass.data[DOMAIN])])


class NooLiteFan(NooLiteGenericModule, FanEntity):

    def __init__(self, config, device):
        super().__init__(config, device)
        self._last_turn_on_percentage = 100
        if config[CONF_SPEED_ENABLED] is True:
            self._attr_speed_count = config[CONF_SPEED_COUNT]
            self._attr_supported_features = SUPPORT_SET_SPEED

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

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        self._attr_percentage = self._level * 100

    def set_direction(self, direction: str) -> None:
        pass

    def set_speed(self, speed: str) -> None:
        pass

    def set_preset_mode(self, preset_mode: str) -> None:
        self.turn_on(preset_mode=preset_mode)

    def oscillate(self, oscillating: bool) -> None:
        pass
