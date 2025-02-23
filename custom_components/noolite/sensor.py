import logging

import voluptuous as vol
from NooLite_F import BatteryState, RemoteController, TempHumiSensor, RGBRemoteController
from homeassistant.const import (CONF_NAME, PERCENTAGE, STATE_ON, STATE_OFF, CONF_TYPE, UnitOfTemperature)
from homeassistant.helpers import config_validation as cv
from homeassistant.components.sensor import (SensorEntity, SensorStateClass, SensorDeviceClass, PLATFORM_SCHEMA)

from .base import (NooLiteGenericSensor, NooLiteGenericRemoteController)
from .const import (CONF_CHANNEL, DOMAIN,
                    TYPE_HUMI, TYPE_TEMP, TYPE_ANALOG, TYPE_REMOTE, DATA_INTERVAL, BATTERY_DATA_INTERVAL, STATE_TUNE_UP,
                    STATE_TUNE_DOWN, STATE_SWITCH, STATE_SAVE_PRESET, STATE_LOAD_PRESET,
                    STATE_ROLL_COLOR, STATE_SWITCH_COLOR, STATE_SWITCH_MODE, STATE_SWITCH_SPEED, TYPE_RGB_REMOTE,
                    LOG_LEVEL, STATE_TUNE_BACK, STATE_TUNE_STOP)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(LOG_LEVEL)

_TYPES = [TYPE_HUMI, TYPE_TEMP, TYPE_ANALOG, TYPE_REMOTE, TYPE_RGB_REMOTE]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(_TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int
})


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
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
        devices.append(NooLiteRemoteController(config, hass.data[DOMAIN]))
    elif module_type == TYPE_RGB_REMOTE:
        devices.append(NooLiteRGBRemoteController(config, hass.data[DOMAIN]))

    add_devices(devices)


class NooLiteTemperatureSensor(NooLiteGenericSensor, SensorEntity):
    def __init__(self, config, device):
        super().__init__(config, device, DATA_INTERVAL)
        self._sensor = TempHumiSensor(device, self._channel, self._on_data)
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
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


class NooLiteRemoteController(NooLiteGenericRemoteController):
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

    def _on_on(self):
        self.set_state(STATE_ON)

    def _on_off(self):
        self.set_state(STATE_OFF)

    def _on_switch(self):
        self.set_state(STATE_SWITCH)

    def _on_load_preset(self):
        self.set_state(STATE_LOAD_PRESET)

    def _on_save_preset(self):
        self.set_state(STATE_SAVE_PRESET)

    def _on_tune_start(self, direction):
        from NooLite_F import Direction
        if direction == Direction.UP:
            self.set_state(STATE_TUNE_UP)
        elif direction == Direction.DOWN:
            self.set_state(STATE_TUNE_DOWN)

    def _on_tune_back(self):
        self.set_state(STATE_TUNE_BACK)

    def _on_tune_stop(self):
        self.set_state(STATE_TUNE_STOP)


class NooLiteRGBRemoteController(NooLiteGenericRemoteController):
    def __init__(self, config, device):
        super().__init__(config, device, BATTERY_DATA_INTERVAL)
        self._sensor = RGBRemoteController(controller=device,
                                           channel=self._channel,
                                           on_switch=self._on_switch,
                                           on_tune_back=self._on_tune_back,
                                           on_tune_stop=self._on_tune_stop,
                                           on_roll_color=self._on_roll_color,
                                           on_switch_color=self._on_switch_color,
                                           on_switch_mode=self._on_switch_mode,
                                           on_switch_speed=self._on_switch_speed,
                                           on_battery_low=self.low_battery)

    def _on_switch(self):
        self.set_state(STATE_SWITCH)

    def _on_tune_back(self):
        self.set_state(STATE_TUNE_BACK)

    def _on_tune_stop(self):
        self.set_state(STATE_TUNE_STOP)

    def _on_roll_color(self):
        self.set_state(STATE_ROLL_COLOR)

    def _on_switch_color(self):
        self.set_state(STATE_SWITCH_COLOR)

    def _on_switch_mode(self):
        self.set_state(STATE_SWITCH_MODE)

    def _on_switch_speed(self):
        self.set_state(STATE_SWITCH_SPEED)
