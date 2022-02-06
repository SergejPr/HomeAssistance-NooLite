import logging
from threading import Timer

import voluptuous as vol
from NooLite_F import BatteryState, RemoteController, TempHumiSensor
from homeassistant.const import CONF_NAME, PERCENTAGE, STATE_ON, \
    STATE_OFF
from homeassistant.const import CONF_TYPE, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.helpers import config_validation as cv
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass

from . import (PLATFORM_SCHEMA)
from .base import (NooLiteGenericSensor)
from .const import (CONF_CHANNEL, DOMAIN,
                    TYPE_HUMI, TYPE_TEMP, TYPE_ANALOG, TYPE_REMOTE, DATA_INTERVAL, BATTERY_DATA_INTERVAL, STATE_TUNE_UP,
                    STATE_TUNE_DOWN, STATE_TUNE, STATE_SWITCH, STATE_SAVE_PRESET, STATE_LOAD_PRESET,
                    REMOTE_SENSOR_RESET_STATE_TIMEOUT)


DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_TYPES = [TYPE_HUMI, TYPE_TEMP, TYPE_ANALOG, TYPE_REMOTE]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(_TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == TYPE_HUMI:
        devices.append(NooLiteHumiditySensor(config, hass.data[DOMAIN]))
    elif module_type == TYPE_TEMP:
        devices.append(NooLiteTemperatureSensor(config, hass.data[DOMAIN]))
    elif module_type == TYPE_ANALOG:
        devices.append(NooLiteAnalogSensor(config, hass.data[DOMAIN]))
    elif module_type == TYPE_REMOTE:
        devices.append(NooLiteRemoteSensor(config, hass.data[DOMAIN]))

    add_devices(devices)


class NooLiteTemperatureSensor(NooLiteGenericSensor, SensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, DATA_INTERVAL)
        self._sensor = TempHumiSensor(device, self._channel, self._on_data)
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._attr_native_value = temp
        self.schedule_update_ha_state()


class NooLiteHumiditySensor(NooLiteGenericSensor, SensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, DATA_INTERVAL)
        self._sensor = TempHumiSensor(device, self._channel, self._on_data)
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._attr_native_value = humi
        self.schedule_update_ha_state()


class NooLiteAnalogSensor(NooLiteGenericSensor, SensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, DATA_INTERVAL)
        self._sensor = TempHumiSensor(device, self._channel, self._on_data)
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._attr_native_value = analog
        self.schedule_update_ha_state()


class NooLiteRemoteSensor(NooLiteGenericSensor):
    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._sensor = RemoteController(controller=device,
                                        channel=self._channel,
                                        on_on=self._on_on,
                                        on_off=self._on_off,
                                        on_switch=self._on_switch,
                                        on_tune_start=self._on_tune_start,
                                        on_tune_back=self._on_tune_back,
                                        on_tune_stop=self._on_tune_stop,
                                        on_load_preset=self._on_load_preset,
                                        on_save_preset=self._on_save_preset,
                                        on_battery_low=self.low_battery)
        self._timer = None

    def _start_timer(self):
        self._cancel_timer()
        self._timer = Timer(REMOTE_SENSOR_RESET_STATE_TIMEOUT, self._reset_state)
        self._timer.start()

    def _cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self.timer = None

    def _reset_state(self):
        self._cancel_timer()
        self._attr_state = STATE_UNKNOWN
        self.schedule_update_ha_state()

    def _on_on(self):
        _LOGGER.debug('remote_sensor on_on')
        self.action_detected()
        self._attr_state = STATE_ON
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_off(self):
        _LOGGER.debug('remote_sensor on_off')
        self.action_detected()
        self._attr_state = STATE_OFF
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_tune_start(self, direction):
        from NooLite_F import Direction
        _LOGGER.debug('remote_sensor on_tune_start. direction {0}'.format(direction))
        self.action_detected()
        if direction == Direction.UP:
            self._attr_state = STATE_TUNE_UP
        elif direction == Direction.DOWN:
            self._attr_state = STATE_TUNE_DOWN
        self.schedule_update_ha_state()

    def _on_tune_back(self):
        _LOGGER.debug('remote_sensor on_tune_back')
        self.action_detected()
        self._attr_state = STATE_TUNE
        self.schedule_update_ha_state()

    def _on_tune_stop(self):
        _LOGGER.debug('remote_sensor on_tune_stop')
        self.action_detected()
        self._reset_state()
        self.schedule_update_ha_state()

    def _on_switch(self):
        _LOGGER.debug('remote_sensor on_switch')
        self.action_detected()
        self._attr_state = STATE_SWITCH
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_load_preset(self):
        _LOGGER.debug('remote_sensor on_load_preset')
        self.action_detected()
        self._attr_state = STATE_LOAD_PRESET
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_save_preset(self):
        _LOGGER.debug('remote_sensor on_save_preset')
        self.action_detected()
        self._attr_state = STATE_SAVE_PRESET
        self.schedule_update_ha_state()
        self._start_timer()

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def force_update(self):
        return True
