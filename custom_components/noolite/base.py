import logging
from threading import Timer

from homeassistant.const import CONF_NAME, CONF_MODE, ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import ToggleEntity, Entity

from .const import (MODE_NOOLITE, CONF_BROADCAST, CONF_CHANNEL, BATTERY_LEVEL_LOW, BATTERY_LEVEL_NORMAL,
                    BATTERY_LEVEL_DISCHARGED)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)


def _module_mode(config):
    from NooLite_F import ModuleMode

    mode = config[CONF_MODE].lower()

    if mode == MODE_NOOLITE:
        module_mode = ModuleMode.NOOLITE
    else:
        module_mode = ModuleMode.NOOLITE_F

    return module_mode


def _is_module_on(module_state) -> bool:
    from NooLite_F import ModuleState
    return module_state.state == ModuleState.ON or module_state.state == ModuleState.TEMPORARY_ON


class NooLiteGenericModule(ToggleEntity):
    def __init__(self, config, device):
        from NooLite_F import ModuleMode
        self._device = device
        self._mode = _module_mode(config)
        self._broadcast = config[CONF_BROADCAST]
        self._channel = config[CONF_CHANNEL]
        self._level = 0.0
        self._attr_assumed_state = self._mode == ModuleMode.NOOLITE
        self._attr_name = config[CONF_NAME]

    def turn_on(self, **kwargs):
        responses = self._device.on(None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_is_on = True
        else:
            self._update_state_from(responses)

    def turn_off(self, **kwargs):
        responses = self._device.off(None, self._channel, self._broadcast, self._mode)
        if self.assumed_state:
            self._attr_is_on = False
        else:
            self._update_state_from(responses)

    def toggle(self, **kwargs) -> None:
        if self.assumed_state:
            super().toggle(**kwargs)
        else:
            responses = self._device.switch(None, self._channel, self._broadcast, self._mode)
            self._update_state_from(responses)

    def update(self):
        _LOGGER.info("!!! update")
        if not self.assumed_state:
            responses = self._device.read_state(None, self._channel, self._broadcast, self._mode)
            self._update_state_from(responses)

    def _update_state_from(self, responses):
        state = False
        level = 0.0
        for (result, info, module_state) in responses:
            if result and module_state is not None and _is_module_on(module_state):
                state = True
                level = max(module_state.brightness, level)
        self._attr_is_on = state
        self._level = level


class NooLiteGenericSensor(Entity):
    def __init__(self, config, device, battery_timeout):
        self._device = device
        self._attr_should_poll = False
        self._attr_name = config[CONF_NAME]
        self._channel = config[CONF_CHANNEL]
        self._battery = None
        self._battery_timer = None
        self._battery_timeout = battery_timeout

    def action_detected(self):
        if self._battery_timer is None:
            self.normal_battery()

    def low_battery(self):
        self._battery = BATTERY_LEVEL_LOW
        self._start_battery_timer()
        self.schedule_update_ha_state()

    def normal_battery(self):
        if self._battery_timer is not None:
            self._battery_timer.cancel()
            self._battery_timer = None
        self._battery = BATTERY_LEVEL_NORMAL
        self.schedule_update_ha_state()

    def _start_battery_timer(self):
        if self._battery_timer is not None:
            self._battery_timer.cancel()
        self._battery_timer = Timer(self._battery_timeout, self._on_battery_timer)
        self._battery_timer.start()

    def _on_battery_timer(self):
        self._battery_timer = None
        self.on_battery_timeout()

    def on_battery_timeout(self):
        self._battery = BATTERY_LEVEL_DISCHARGED
        self._attr_state = None
        self.schedule_update_ha_state()

    @property
    def battery(self):
        return self._battery

    @property
    def extra_state_attributes(self):
        attr = {
            ATTR_BATTERY_LEVEL: self._battery
        }
        return attr

    def update(self):
        pass
