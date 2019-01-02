import logging
import voluptuous as vol
import time
from typing import Optional

from threading import Timer

from homeassistant.const import CONF_TYPE, STATE_OFF, STATE_ON
from homeassistant.const import CONF_NAME, CONF_MODE
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers import config_validation as cv

from custom_components import NooLite
from custom_components.NooLite import PLATFORM_SCHEMA
from custom_components.NooLite import CONF_CHANNEL


DEPENDENCIES = ['NooLite']

_LOGGER = logging.getLogger(__name__)

TYPES = ['Motion', 'Remote']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, 'Motion'): vol.In(TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config.get(CONF_TYPE)

    devices = []
    if module_type == 'Motion':
        devices.append(NooLiteMotionSensor(config))
    elif module_type == 'Remote':
        devices.append(NooLiteBinarySensor(config, 'power'))

    add_devices(devices)


class NooLiteMotionSensor(BinarySensorDevice):

    def __init__(self, config):
        from NooLite_F import MotionSensor
        self._config = config
        self._sensor = MotionSensor(NooLite.DEVICE, config.get(CONF_CHANNEL), self._on_motion)
        self._time = time.time()
        self._timer = None

    def _on_motion(self, duration):
        self._time = time.time() + duration*5
        self.schedule_update_ha_state()

        if self._timer is not None:
            self._timer.cancel()
        self._timer = Timer(duration * 5 + 5, self._reset_motion)
        self._timer.start()

    def _reset_motion(self):
        self._timer.cancel()
        self._timer = None
        self._time = time.time()
        self.schedule_update_ha_state()

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return "motion"

    @property
    def should_poll(self):
        """No polling needed for a demo binary sensor."""
        return False

    @property
    def name(self):
        return self._config.get(CONF_NAME)

    @property
    def is_on(self):
        return time.time() < self._time

    def update(self):
        pass


class NooLiteBinarySensor(BinarySensorDevice):

    def __init__(self, config, device_class):
        from NooLite_F import RemoteController
        self._config = config
        self._sensor_type = device_class
        self._sensor = RemoteController(NooLite.DEVICE, config.get(CONF_CHANNEL), self._on_on, self._on_off,
                                        self._on_switch, None, None, None, self._on_load_preset, None, None)
        self._time = time.time()
        self._timer = None
        self._state_on = False

    def _on_on(self):
        self._switch_on()
        self.schedule_update_ha_state()

        if self._timer is not None:
            self._timer.cancel()
        """keep active state for 200ms"""
        self._timer = Timer(0.2, self._switch_off)
        self._timer.start()

    def _on_off(self):
        self._timer.cancel()
        self._timer = None
        self._switch_off()
        self.schedule_update_ha_state()

    def _switch_on(self):
        self._state_on = True

    def _switch_off(self):
        self._state_on = False
        self.schedule_update_ha_state()

    def _on_switch(self):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
        self._switch_on() if not self.is_on else self._switch_off()
        self.schedule_update_ha_state()

    def _on_load_preset(self):
        self._on_on()

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state_on

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def name(self) -> Optional[str]:
        """Return the name of the entity."""
        return self._config.get(CONF_NAME)
