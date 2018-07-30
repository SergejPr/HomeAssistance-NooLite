import logging
import voluptuous as vol

from homeassistant.const import CONF_TYPE, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from custom_components.NooLite import PLATFORM_SCHEMA
from custom_components.NooLite import CONF_CHANNEL, CONF_NAME, CONF_MODE
from custom_components import NooLite
from homeassistant.helpers import config_validation as cv

DEPENDENCIES = ['NooLite']

_LOGGER = logging.getLogger(__name__)

TYPES = ['TempHumi', 'Temp', 'Analog']

MEASUREMENT_PERCENTS = "%"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(TYPES),
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_CHANNEL): cv.positive_int,
    vol.Required(CONF_MODE): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NooLite platform."""
    _LOGGER.info(config)

    module_type = config.get(CONF_TYPE)

    devices = []
    if module_type == 'TempHumi':
        devices.append(NooLiteHumiSensor(hass, config))
        devices.append(NooLiteTempSensor(hass, config))
    elif module_type == 'Temp':
        devices.append(NooLiteTempSensor(hass, config))
    elif module_type == 'Analog':
        devices.append(NooLiteAnalogSensor(hass, config))

    add_devices(devices)


class NooLiteSensor(Entity):
    def __init__(self, hass, config):
        self._config = config
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        return self._config.get(CONF_NAME)

    @property
    def config(self):
        return self._config

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        return False

    def update(self):
        pass


class NooLiteTempSensor(NooLiteSensor):

    def __init__(self, hass, config):
        super().__init__(hass, config)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(NooLite.DEVICE, config.get(CONF_CHANNEL), self._on_data)

    def _on_data(self, temp, humi, battery, analog):
        self._state = temp
        self.schedule_update_ha_state()

    @property
    def name(self):
        return super().name + "_temp"

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS


class NooLiteHumiSensor(NooLiteSensor):

    def __init__(self, hass, config):
        super().__init__(hass, config)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(NooLite.DEVICE, config.get(CONF_CHANNEL), self._on_data)

    def _on_data(self, temp, humi, battery, analog):
        self._state = humi
        self.schedule_update_ha_state()

    @property
    def name(self):
        return super().name + "_humi"

    @property
    def unit_of_measurement(self):
        return MEASUREMENT_PERCENTS


class NooLiteAnalogSensor(NooLiteSensor):
    def __init__(self, hass, config):
        super().__init__(hass, config)
        from NooLite_F import TempHumiSensor
        self._sensor = TempHumiSensor(NooLite.DEVICE, config.get(CONF_CHANNEL), self._on_data)

    def _on_data(self, temp, humi, battery, analog):
        self._state = analog
        self.schedule_update_ha_state()

    @property
    def name(self):
        return super().name + "_analog"

    @property
    def unit_of_measurement(self):
        return ""
