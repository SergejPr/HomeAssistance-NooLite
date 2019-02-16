import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.fan import (FanEntity, SUPPORT_SET_SPEED, SUPPORT_OSCILLATE, SUPPORT_DIRECTION,
                                          SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH, SPEED_OFF)
from homeassistant.const import CONF_NAME, CONF_MODE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from custom_components.noolite import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F,
                                       NooLiteGenericModule, DOMAIN)
from custom_components.noolite import (PLATFORM_SCHEMA)

FULL_SUPPORT = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
LIMITED_SUPPORT = SUPPORT_SET_SPEED

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=_SCAN_INTERVAL): cv.time_period,
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
        self._speed = SPEED_OFF

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [SPEED_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        # TODO: Check speed feature. Seems for it should be returned 1
        return 0

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the entity."""
        if speed is None:
            speed = SPEED_MEDIUM
        self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self.set_speed(SPEED_OFF)

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if speed is None:
            speed = self._speed

        if speed == SPEED_HIGH:
            int_speed = 255
        elif speed == SPEED_MEDIUM:
            int_speed = 180
        elif speed == SPEED_LOW:
            int_speed = 70
        else:
            int_speed = 0

        responses = self._device.set_brightness(int_speed / 255, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._state = speed != SPEED_OFF
            self._speed = speed
        else:
            self._update_state_from(responses)

        self.schedule_update_ha_state()

    def set_direction(self, direction: str) -> None:
        pass

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        int_speed = int(self._level * 255)

        if 0 < int_speed <= 80:
            self._speed = SPEED_LOW
        elif 80 < int_speed <= 180:
            self._speed = SPEED_MEDIUM
        elif 180 < int_speed:
            self._speed = SPEED_HIGH
        else:
            self._speed = SPEED_OFF
