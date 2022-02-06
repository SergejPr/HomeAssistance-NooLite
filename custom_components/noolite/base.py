import logging
from threading import Timer

from homeassistant.const import CONF_NAME, CONF_MODE, ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import ToggleEntity, Entity

from .const import (MODE_NOOLITE, CONF_BROADCAST, CONF_CHANNEL, BATTERY_LEVEL_LOW, BATTERY_LEVEL_NORMAL,
                    BATTERY_LEVEL_DISCHARGED)


_LOGGER = logging.getLogger(__name__)


def _module_mode(config):
    from NooLite_F import ModuleMode

    mode = config[CONF_MODE].lower()

    if mode == MODE_NOOLITE:
        mode_enum_value = ModuleMode.NOOLITE
    else:
        mode_enum_value = ModuleMode.NOOLITE_F

    return mode_enum_value


def _is_module_on(module_state) -> bool:
    from NooLite_F import ModuleState
    return module_state.state == ModuleState.ON or module_state.state == ModuleState.TEMPORARY_ON


def should_pull_on_start(config) -> bool:
    from NooLite_F import ModuleMode
    return _module_mode(config) == ModuleMode.NOOLITE_F


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
        self._ignore_next_update = False

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
        # HA calls update method after execution any command to sync state,
        # but for Noolite-F we update state from command response, so ignore update after command
        # to decrease requests count
        if self._ignore_next_update:
            self._ignore_next_update = False
            return

        if not self.assumed_state:
            responses = self._device.read_state(None, self._channel, self._broadcast, self._mode)
            self._update_state_from(responses, False)

    def _update_state_from(self, responses, ignore_next=True):
        state = None
        level = 0.0

        for (result, info, module_state) in responses:
            if result and module_state is not None:
                is_module_on = _is_module_on(module_state)
                if is_module_on:
                    state = True
                    level = max(module_state.brightness, level)
                elif state is None:
                    state = False

        self._attr_is_on = state
        self._level = level

        # if state is None (can't receive response/module state) then don't ignore next update
        # to give one more chance to receive data
        self._ignore_next_update = state is not None and ignore_next


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
