"""
Support for NooLite.
"""

import logging

import voluptuous as vol
from homeassistant.const import CONF_PORT
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_BAUDRATE, DEFAULT_PORT
from NooLite_F.MTRF64.MTRF64Adapter import DEFAULT_BAUDRATE

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the connection to the NooLite device."""

    from NooLite_F.MTRF64 import MTRF64Controller
    from serial import SerialException

    try:
        hass.data[DOMAIN] = MTRF64Controller(config[DOMAIN][CONF_PORT], config[DOMAIN][CONF_BAUDRATE])
    except SerialException as exc:
        _LOGGER.error("Unable to open serial port for NooLite: %s", exc)
        return False
    except KeyError as exc:
        _LOGGER.error("Configuration for NooLite component doesn't found: %s", exc)
        return False

    def _release_noolite():
        hass.data[DOMAIN].release()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, _release_noolite)

    return True
