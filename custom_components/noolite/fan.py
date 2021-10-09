import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.components.fan import (FanEntity, SUPPORT_SET_SPEED, SUPPORT_PRESET_MODE)
from homeassistant.const import CONF_NAME, CONF_MODE, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from custom_components.noolite import (CONF_BROADCAST, CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F,
                                       NooLiteGenericModule, DOMAIN)
from custom_components.noolite import (PLATFORM_SCHEMA)

DEPENDENCIES = ['noolite']

CONF_SPEED_ENABLED = "speed_enabled"

_LOGGER = logging.getLogger(__name__)

_SCAN_INTERVAL = timedelta(seconds=60)
_DEFAULT_SPEED = 50

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_BROADCAST, default=False): cv.boolean,
    vol.Optional(CONF_SCAN_INTERVAL, default=_SCAN_INTERVAL): cv.time_period,
    vol.Optional(CONF_SPEED_ENABLED, default=False): cv.boolean,
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
        self._speed_mode = config[CONF_SPEED_ENABLED]
        self._percentage = _DEFAULT_SPEED

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        if self._speed_mode is True:
            return SUPPORT_SET_SPEED | SUPPORT_PRESET_MODE
        else:
            return 0

    def turn_on(self, percentage: int, **kwargs) -> None:
        """Turn on the entity."""
        if percentage is None:
            percentage = self._percentage
        self.set_percentage(percentage)

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self.set_percentage(0)

    def set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan."""
        if percentage is None:
            percentage = self._percentage

        responses = self._device.set_brightness(percentage / 100, None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._state = percentage != 0
            self._percentage = percentage
        else:
            self._update_state_from(responses)

        self.schedule_update_ha_state()

    @property
    def percentage(self) -> int:
        return self._percentage

    def set_direction(self, direction: str) -> None:
        pass

    def _update_state_from(self, responses):
        super()._update_state_from(responses)
        self._percentage = self._level * 100
