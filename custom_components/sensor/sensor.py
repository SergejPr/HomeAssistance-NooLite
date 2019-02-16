import logging
import time
from threading import Timer

import voluptuous as vol
from NooLite_F import BatteryState
from homeassistant.const import CONF_NAME, CONF_MODE, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY
from homeassistant.const import CONF_TYPE, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.helpers import config_validation as cv

from custom_components import noolite
from custom_components.noolite import CONF_CHANNEL, MODES_NOOLITE, MODE_NOOLITE_F, NooLiteGenericSensor
from custom_components.noolite import PLATFORM_SCHEMA

DEPENDENCIES = ['noolite']

_LOGGER = logging.getLogger(__name__)

_TYPE_TEMP = 'temp'
_TYPE_HUMI = 'humi'
_TYPE_ANALOG = 'analog'
_TYPE_REMOTE = 'remote'

_TYPES = [_TYPE_HUMI, _TYPE_TEMP, _TYPE_ANALOG, _TYPE_REMOTE]

_DATA_INTERVAL = 1.5 * 60 * 60

_BATTERY_DATA_INTERVAL = 6 * 60 * 60

MEASUREMENT_PERCENTS = "%"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(_TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE, default=MODE_NOOLITE_F): vol.In(MODES_NOOLITE),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config[CONF_TYPE].lower()

    devices = []
    if module_type == _TYPE_HUMI:
        devices.append(NooLiteHumiditySensor(config))
    elif module_type == _TYPE_TEMP:
        devices.append(NooLiteTemperatureSensor(config))
    elif module_type == _TYPE_ANALOG:
        devices.append(NooLiteAnalogSensor(config))
    elif module_type == _TYPE_REMOTE:
        devices.append(NooLiteRemoteSensor(config))

    add_devices(devices)


class NooLiteTemperatureSensor(NooLiteGenericSensor):
    def __init__(self, config):
        super().__init__(config, _DATA_INTERVAL)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(noolite.DEVICE, self._channel, self._on_data)

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._state = temp
        self.schedule_update_ha_state()

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def state(self):
        return self._state


class NooLiteHumiditySensor(NooLiteGenericSensor):
    def __init__(self, config):
        super().__init__(config, _DATA_INTERVAL)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(noolite.DEVICE, self._channel, self._on_data)

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._state = humi
        self.schedule_update_ha_state()

    @property
    def unit_of_measurement(self):
        return MEASUREMENT_PERCENTS

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY

    @property
    def state(self):
        return self._state


class NooLiteAnalogSensor(NooLiteGenericSensor):
    def __init__(self, config):
        super().__init__(config, _DATA_INTERVAL)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(noolite.DEVICE, self._channel, self._on_data)

    def _on_data(self, temp, humi, analog, battery):
        if battery == BatteryState.OK:
            self.normal_battery()
        else:
            self.low_battery()
        self._state = analog
        self.schedule_update_ha_state()

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def state(self):
        return self._state


class NooLiteRemoteSensor(NooLiteGenericSensor):
    def __init__(self, config):
        super().__init__(config, _BATTERY_DATA_INTERVAL)
        from NooLite_F import RemoteController
        self._config = config
        self._sensor = RemoteController(controller=noolite.DEVICE,
                                        channel=config.get(CONF_CHANNEL),
                                        on_on=self._on_on,
                                        on_off=self._on_off,
                                        on_switch=self.action_detected,
                                        on_tune_start=self._on_tune_start,
                                        on_tune_back=self._on_tune_back,
                                        on_tune_stop=self._on_tune_stop,
                                        on_load_preset=self.action_detected,
                                        on_save_preset=self.action_detected,
                                        on_battery_low=self.low_battery)
        self._timer = None

    def _start_timer(self):
        self._cancel_timer()
        self._timer = Timer(0.2, self._reset_state)
        self._timer.start()

    def _cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
        self.timer = None

    def _reset_state(self):
        self._cancel_timer()
        self._state = STATE_UNKNOWN
        self.schedule_update_ha_state()

    def _on_on(self):
        _LOGGER.debug('remote_sensor on_on')
        self.action_detected()
        self._state = 'ON'
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_off(self):
        _LOGGER.debug('remote_sensor on_off')
        self.action_detected()
        self._state = "OFF"
        self.schedule_update_ha_state()
        self._start_timer()

    def _on_tune_start(self, direction):
        from NooLite_F import Direction
        _LOGGER.debug('remote_sensor on_tune_start. direction {0}'.format(direction))
        self.action_detected()
        if direction == Direction.UP:
            self._state = 'UP'
        elif direction == Direction.DOWN:
            self._state = 'DOWN'
        self.schedule_update_ha_state()

    def _on_tune_back(self):
        _LOGGER.debug('remote_sensor on_tune_back')
        self.action_detected()

    def _on_tune_stop(self):
        _LOGGER.debug('remote_sensor on_tune_stop')
        self.action_detected()
        self._state = "STOP"
        self.schedule_update_ha_state()
        self._start_timer()

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def force_update(self):
        return True

    @property
    def state(self):
        return self._state
