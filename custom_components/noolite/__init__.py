"""
Support for NooLite.
"""

import logging

import voluptuous as vol
from homeassistant.const import CONF_PORT
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

PLATFORM_SCHEMA = vol.Schema({
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the connection to the NooLite device."""

    from NooLite_F.MTRF64 import MTRF64Controller
    from serial import SerialException

    try:
        hass.data[DOMAIN] = MTRF64Controller(config[DOMAIN][CONF_PORT])
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
