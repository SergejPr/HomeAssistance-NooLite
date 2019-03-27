# HomeAssistance-NooLite
NooLite platform for Home Assistance 

**Note:** version 0.1.+ supported only in HA 8.16.0 and above. It is related to changing of the custom component architecture.

Changelog:
==========

v0.1.0
------

* added binary sensors for: door, garage_door, moisture, opening, window, light, motion, battery (in noolite remotes)
* added battery level information

**Breaking changes:**

* platform and type names in config now is in lowercase
* removed unused types
* TempHumi sensor split to two separate sensors: temp and humi


Supported entities:
===================

Binary sensor:
--------------
type:
++++++
* door
* garage_door
* moisture
* opening
* window
* light
* motion
* battery (in noolite remotes)
* remote (for noolite remotes, support on, off, switch and load_preset events)


Sensor:
-------
type:
+++++
* temp
* humi
* analog
* remote (for noolite remotes, support on, off, tune start and tune stop events)


Light:
------
type:
+++++
* light (for module without dimmer)
* dimmer (for module with dimmer)
* rgb_led (for rgb module)


Fan:
----

Switch:
-------



