import logging

import voluptuous as vol
from datetime import timedelta


LOG_LEVEL = logging.WARNING

DOMAIN = 'noolite'

DEFAULT_PORT = '/dev/ttyUSB0'

MODE_NOOLITE = 'noolite'
MODE_NOOLITE_F = 'noolite-f'

MODES_NOOLITE = [MODE_NOOLITE, MODE_NOOLITE_F]

BATTERY_LEVEL_NORMAL = 100
BATTERY_LEVEL_LOW = 20
BATTERY_LEVEL_DISCHARGED = 0

DEVICE_CLASS_DIMMER = 'noolite_dimmer'
DEVICE_CLASS_RGB = 'noolite_rgb'
DEVICE_CLASS_FAN = 'noolite_fan'
DEVICE_CLASS_SWITCH = 'noolite_switch'

CONF_BAUDRATE = 'baudrate'
CONF_CHANNEL = 'channel'
CONF_BROADCAST = 'broadcast'
CONF_SPEED_ENABLED = 'speed_enabled'
CONF_SPEED_COUNT = 'speed_count'

SCAN_INTERVAL = timedelta(seconds=60)
DATA_INTERVAL = 1.5 * 60 * 60
BINARY_SENSOR_DATA_INTERVAL = 13 * 60 * 60
BATTERY_DATA_INTERVAL = 6 * 60 * 60

TYPE_LIGHT = 'light'
TYPE_DIMMER = 'dimmer'
TYPE_RGB_LED = 'rgb_led'
TYPE_DOOR = 'door'
TYPE_GARAGE_DOOR = 'garage_door'
TYPE_MOISTURE = 'moisture'
TYPE_OPENING = 'opening'
TYPE_WINDOW = 'window'
TYPE_MOTION = 'motion'
TYPE_BATTERY = 'battery'
TYPE_TEMP = 'temp'
TYPE_HUMI = 'humi'
TYPE_ANALOG = 'analog'

TYPE_REMOTE = 'remote'
TYPE_RGB_REMOTE = 'rgb_remote'

STATE_TUNE_BACK = 'tune_back'
STATE_TUNE_UP = 'tune_up'
STATE_TUNE_DOWN = 'tune_down'
STATE_TUNE_STOP = 'tune_stop'

STATE_SWITCH = 'switch'
STATE_LOAD_PRESET = 'load_preset'
STATE_SAVE_PRESET = 'save_preset'
STATE_ROLL_COLOR = 'roll_color'
STATE_SWITCH_COLOR = 'switch_color'
STATE_SWITCH_MODE = 'switch_mode'
STATE_SWITCH_SPEED = 'switch_speed'

REMOTE_CONTROL_RESET_STATE_TIMEOUT = 0.2

TUNE_DIRECTION_UP = "Up"
TUNE_DIRECTION_DOWN = "Down"
TUNE_DIRECTION_REVERSE = "Reverse"

TUNE_DIRECTION_FIELD = "direction"
TUNE_DIRECTION_VALUES = [TUNE_DIRECTION_UP, TUNE_DIRECTION_DOWN, TUNE_DIRECTION_REVERSE]

TUNE_SCHEMA = {
    vol.Required(TUNE_DIRECTION_FIELD): vol.In(TUNE_DIRECTION_VALUES),
}
