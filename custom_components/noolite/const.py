from datetime import timedelta

DOMAIN = 'noolite'

DEFAULT_PORT = '/dev/ttyUSB0'

MODE_NOOLITE = 'noolite'
MODE_NOOLITE_F = 'noolite-f'

MODES_NOOLITE = [MODE_NOOLITE, MODE_NOOLITE_F]

BATTERY_LEVEL_NORMAL = 100
BATTERY_LEVEL_LOW = 20
BATTERY_LEVEL_DISCHARGED = 0

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
TYPE_REMOTE = 'remote'
TYPE_TEMP = 'temp'
TYPE_HUMI = 'humi'
TYPE_ANALOG = 'analog'

STATE_TUNE = 'tune'
STATE_TUNE_UP = 'tune_up'
STATE_TUNE_DOWN = 'tune_down'

STATE_SWITCH = 'switch'
STATE_LOAD_PRESET = 'load_preset'
STATE_SAVE_PRESET = 'save_preset'

REMOTE_SENSOR_RESET_STATE_TIMEOUT = 0.2
