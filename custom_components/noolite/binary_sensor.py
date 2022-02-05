import logging
import time
from threading import Timer

import voluptuous as vol
from NooLite_F import RemoteController, MotionSensor, Direction, BatteryState
from NooLite_F.Sensors import BinarySensor, GenericListener
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.const import CONF_TYPE
from homeassistant.helpers import config_validation as cv

from . import (PLATFORM_SCHEMA)
from .base import (NooLiteGenericSensor)
from .const import (CONF_CHANNEL, BATTERY_LEVEL_DISCHARGED, BATTERY_LEVEL_NORMAL, DOMAIN,
                    TYPE_MOTION, TYPE_BATTERY, TYPE_DOOR, TYPE_GARAGE_DOOR, TYPE_MOISTURE, TYPE_OPENING, TYPE_WINDOW,
                    TYPE_LIGHT, TYPE_REMOTE, BATTERY_DATA_INTERVAL, BINARY_SENSOR_DATA_INTERVAL)

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_TYPES = [TYPE_MOTION, TYPE_BATTERY, TYPE_DOOR, TYPE_GARAGE_DOOR, TYPE_MOISTURE, TYPE_OPENING, TYPE_WINDOW,
          TYPE_LIGHT, TYPE_REMOTE]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_TYPE, default=TYPE_OPENING): vol.In(_TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == TYPE_MOTION:
        devices.append(NooLiteMotionSensor(config, hass.data[DOMAIN]))
    elif module_type == TYPE_BATTERY:
        devices.append(NooLiteBatterySensor(config, hass.data[DOMAIN]))
    elif module_type == TYPE_REMOTE:
        devices.append(NooLiteRemoteSensor(config, hass.data[DOMAIN]))
    else:
        devices.append(NooLiteBinarySensor(config, hass.data[DOMAIN]))

    add_devices(devices)


class NooLiteBatterySensor(NooLiteGenericSensor, BinarySensorEntity):
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

    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._sensor = self.Receiver(device, self._channel, self.action_detected, self.low_battery,
                                     self.normal_battery)

    @property
    def device_class(self):
        return "battery"

    @property
    def is_on(self):
        return self.battery != BATTERY_LEVEL_NORMAL


class NooLiteMotionSensor(NooLiteGenericSensor, BinarySensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._sensor = MotionSensor(device, self._channel, self._on_motion, self.low_battery)
        self._time = time.time()
        self._timer = None

    def _on_motion(self, duration):
        self._time = time.time() + duration * 5
        self._start_timer(duration * 5 + 5)
        self.action_detected()
        self.schedule_update_ha_state()

    def _start_timer(self, duration):
        self._cancel_timer()
        self._timer = Timer(duration, self._reset_motion)
        self._timer.start()

    def _cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self.timer = None

    def _reset_motion(self):
        self._cancel_timer()
        self._time = time.time()
        self.schedule_update_ha_state()

    @property
    def device_class(self):
        return "motion"

    @property
    def is_on(self):
        return time.time() < self._time


class NooLiteBinarySensor(NooLiteGenericSensor, BinarySensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._device_class = config[CONF_TYPE]
        self._sensor = BinarySensor(device, self._channel, self._on_on, self._on_off, self.low_battery)
        self._timer = None

    def _on_on(self):
        self._attr_is_on = True
        self.action_detected()
        self.schedule_update_ha_state()

    def _on_off(self):
        self._attr_is_on = False
        self.action_detected()
        self.schedule_update_ha_state()

    def _start_timer(self):
        self._cancel_timer()
        self._timer = Timer(BINARY_SENSOR_DATA_INTERVAL, self._on_timer)
        self._timer.start()

    def _cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self.timer = None

    def _on_timer(self):
        self._cancel_timer()
        self._attr_is_on = None
        self._battery = BATTERY_LEVEL_DISCHARGED
        self.schedule_update_ha_state()

    def on_battery_timeout(self):
        pass

    @property
    def device_class(self):
        return self._device_class


class NooLiteRemoteSensor(NooLiteGenericSensor, BinarySensorEntity):

    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._sensor = RemoteController(controller=device,
                                        channel=self._channel,
                                        on_on=self._on_on,
                                        on_off=self._on_off,
                                        on_switch=None,
                                        on_tune_start=None,
                                        on_tune_back=None,
                                        on_tune_stop=None,
                                        on_load_preset=None,
                                        on_save_preset=None,
                                        on_battery_low=self.low_battery)

    def _on_on(self):
        self._attr_is_on = True
        self.schedule_update_ha_state()
        self.action_detected()

    def _on_off(self):
        self._attr_is_on = False
        self.schedule_update_ha_state()
        self.action_detected()

    @property
    def device_class(self):
        return "remote"
