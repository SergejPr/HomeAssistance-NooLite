import logging
import time
from threading import Timer

import voluptuous as vol
from NooLite_F import RemoteController, MotionSensor, Direction, BatteryState
from NooLite_F.Sensors import BinarySensor, GenericListener
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import CONF_NAME, CONF_MODE, STATE_UNKNOWN, STATE_ON, STATE_OFF
from homeassistant.const import CONF_TYPE
from homeassistant.helpers import config_validation as cv

from custom_components import noolite
from custom_components.noolite import CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, BATTERY_LEVEL_DISCHARGED, \
    BATTERY_LEVEL_NORMAL, NooLiteGenericSensor
from custom_components.noolite import PLATFORM_SCHEMA

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_TYPE_DOOR = 'door'
_TYPE_GARAGE_DOOR = 'garage_door'
_TYPE_MOISTURE = 'moisture'
_TYPE_OPENING = 'opening'
_TYPE_WINDOW = 'window'
_TYPE_LIGHT = 'light'
_TYPE_MOTION = 'motion'
_TYPE_BATTERY = 'battery'
_TYPE_REMOTE = 'remote'

_TYPES = [_TYPE_MOTION, _TYPE_BATTERY, _TYPE_DOOR, _TYPE_GARAGE_DOOR, _TYPE_MOISTURE, _TYPE_OPENING, _TYPE_WINDOW,
          _TYPE_LIGHT, _TYPE_REMOTE]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default=_TYPE_OPENING): vol.In(_TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})

_DATA_INTERVAL = 13 * 60 * 60
_BATTERY_DATA_INTERVAL = 6 * 60 * 60


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == _TYPE_MOTION:
        devices.append(NooLiteMotionSensor(config))
    elif module_type == _TYPE_BATTERY:
        devices.append(NooLiteBatterySensor(config))
    elif module_type == _TYPE_REMOTE:
        devices.append(NooLiteRemoteSensor(config))
    else:
        devices.append(NooLiteBinarySensor(config))

    add_devices(devices)


class NooLiteBatterySensor(NooLiteGenericSensor, BinarySensorDevice):
    class Receiver(GenericListener):
        def __init__(self, controller, channel, on_action, on_battery_low, on_battery_normal):
            super().__init__(controller, channel, on_battery_low)
            self._on_action = on_action
            self._on_battery_low = on_battery_low
            self._on_battery_normal = on_battery_normal

        def on_on(self):
            self._on_action()

        def on_off(self):
            self._on_action()

        def on_switch(self):
            self._on_action()

        def on_load_preset(self):
            self._on_action()

        def on_save_preset(self):
            self._on_action()

        def on_temporary_on(self, duration: int):
            self._on_action()

        def on_brightness_tune(self, direction: Direction):
            self._on_action()

        def on_brightness_tune_back(self):
            self._on_action()

        def on_brightness_tune_stop(self):
            self._on_action()

        def on_brightness_tune_custom(self, direction: Direction, speed: float):
            self._on_action()

        def on_brightness_tune_step(self, direction: Direction, step: int = None):
            self._on_action()

        def on_set_brightness(self, brightness: float):
            self._on_action()

        def on_roll_rgb_color(self):
            self._on_action()

        def on_switch_rgb_color(self):
            self._on_action()

        def on_switch_rgb_mode(self):
            self._on_action()

        def on_switch_rgb_mode_speed(self):
            self._on_action()

        def on_set_rgb_brightness(self, red: float, green: float, blue: float):
            self._on_action()

        def on_temp_humi(self, temp: float, humi: int, battery: BatteryState, analog: float):
            if battery == BatteryState.OK:
                self._on_battery_normal()
            else:
                self._on_battery_low()

    def __init__(self, config):
        super().__init__(config, _BATTERY_DATA_INTERVAL)
        self._sensor = self.Receiver(noolite.DEVICE, self._channel, self.action_detected, self.low_battery,
                                     self.normal_battery)

    @property
    def device_class(self):
        return "battery"

    @property
    def state_attributes(self):
        return None

    @property
    def is_on(self):
        return self.battery != BATTERY_LEVEL_NORMAL


class NooLiteMotionSensor(NooLiteGenericSensor, BinarySensorDevice):
    def __init__(self, config):
        super().__init__(config, _BATTERY_DATA_INTERVAL)
        self._sensor = MotionSensor(noolite.DEVICE, self._channel, self._on_motion, self.low_battery)
        self._time = time.time()
        self._timer = None

    def _on_motion(self, duration):
        self._time = time.time() + duration * 5
        self._start_timer(duration * 5 + 5)
        self.action_detected()
        self.schedule_update_ha_state()

    def _start_timer(self, duration):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = Timer(duration, self._reset_motion)
        self._timer.start()

    def _reset_motion(self):
        self._timer.cancel()
        self._timer = None
        self._time = time.time()
        self.schedule_update_ha_state()

    @property
    def device_class(self):
        return "motion"

    @property
    def is_on(self):
        return time.time() < self._time


class NooLiteBinarySensor(NooLiteGenericSensor, BinarySensorDevice):
    def __init__(self, config):
        super().__init__(config, _BATTERY_DATA_INTERVAL)
        self._device_class = config[CONF_TYPE]
        self._sensor = BinarySensor(noolite.DEVICE, self._channel, self._on_on, self._on_off, self.low_battery)
        self._timer = None

    def _on_on(self):
        self._state = True
        self.action_detected()
        self.schedule_update_ha_state()

    def _on_off(self):
        self._state = False
        self.action_detected()
        self.schedule_update_ha_state()

    def _start_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = Timer(_DATA_INTERVAL, self._on_timer)
        self._timer.start()

    def _on_timer(self):
        self._state = None
        self._battery = BATTERY_LEVEL_DISCHARGED
        self._timer.cancel()
        self._timer = None
        self.schedule_update_ha_state()

    def on_battery_timeout(self):
        pass

    @property
    def device_class(self):
        return self._device_class

    @property
    def is_on(self):
        return self._state


class NooLiteRemoteSensor(NooLiteGenericSensor, BinarySensorDevice):

    def __init__(self, config):
        super().__init__(config, _BATTERY_DATA_INTERVAL)
        self._sensor = RemoteController(controller=noolite.DEVICE,
                                        channel=self._channel,
                                        on_on=self._on_on,
                                        on_off=self._on_off,
                                        on_switch=self._on_switch,
                                        on_tune_start=self.action_detected,
                                        on_tune_back=self.action_detected,
                                        on_tune_stop=self.action_detected,
                                        on_load_preset=self._on_load_preset,
                                        on_save_preset=self.action_detected,
                                        on_battery_low=self.low_battery)
        self._timer = None

    def _on_on(self):
        self.action_detected()
        self._switch_on()
        self.schedule_update_ha_state()

        if self._timer is not None:
            self._timer.cancel()
        """keep active state for 200ms"""
        self._timer = Timer(0.2, self._switch_off)
        self._timer.start()

    def _on_off(self):
        self.action_detected()
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
        self._switch_off()
        self.schedule_update_ha_state()

    def _switch_on(self):
        self._state = True

    def _switch_off(self):
        self._state = False
        self.schedule_update_ha_state()

    def _on_switch(self):
        self.action_detected()
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
        self._switch_on() if not self.is_on else self._switch_off()
        self.schedule_update_ha_state()

    def _on_load_preset(self):
        self._on_on()

    @property
    def device_class(self):
        return "remote"

    @property
    def is_on(self):
        return self._state
