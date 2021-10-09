HomeAssistance-NooLite
======================

NooLite platform for Home Assistance

**Note:** Currently supported only MTRF adapters.

**Note:** version 0.1.+ supported only in HA 8.16.0 and above. It is related to changing of the custom component architecture.


Installation
============

* Copy `custom_components` folder from this repo into your Home Assistant config folder.


Platform configuration
======================

Add next rows to `Configuration.yaml`::

    noolite:
      port: "port_name"

where `port_name` is your NooLite adapter port:

* for Windows it is `COM0`, `COM1`, etc.
* fot Linux it is `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.


Modules configuration
=====================

**Note:** Modules should be already bind with your NooLite adapter. You can use official [nooLite One](https://noo.by/poddergka/skachat.html) application for that.


Binary sensor
-------------
Create file `binary_sensors.yaml`.

Add next line to `Configuration.yaml`::

    binary_sensor: !include binary_sensors.yaml

For each binary sensor add configuration to `binary_sensors.yaml`::

      - name: "sensor_name"
        platform: noolite
        channel: channel_number
        type: sensor_type


where

* sensor_name - name of sensor, e.g. "hall_motion"
* channel_number - channel number on which this sensor was binding
* sensor_type - type of sensor:

  + door
  + garage_door
  + moisture
  + opening
  + window
  + light
  + motion
  + battery (in noolite remotes)
  + remote (for noolite remotes, support on, off, switch and load_preset events)

You can see example in file `binary_sensors.yaml`


Sensor
------

Create file `sensors.yaml`.

Add next line to `Configuration.yaml`::

    sensor: !include sensors.yaml

For each sensor add configuration to `sensors.yaml`::

      - name: "sensor_name"
        platform: noolite
        channel: channel_number
        type: sensor_type


where

* sensor_name - name of sensor, e.g. "hall_temp"
* channel_number - channel number on which this sensor was binding
* sensor_type - type of sensor:

  + temp - temperature sensor
  + humi - humidity sensor
  + analog - analog input value (for more details see https://noo.by/images/downloads/noolite-api_v1-0.pdf)
  + remote - noolite remotes, support on, off, tune start and tune stop events)

You can see example in file `sensors.yaml`


Light
-----

Create file `lights.yaml`.

Add next line to `Configuration.yaml`::

    light: !include lights.yaml

For each light add configuration to `lights.yaml`::

    - name: "light_name"
      platform: noolite
      channel: channel_number
      type: light_type
      mode: module_mode
      scan_interval: scan_interval_value
      broadcast: broadcast_value

where

* light_name - name of light, e.g. "hall_light"
* channel_number - channel number on which this sensor was binding
* light_type - type of module:

  + light - for module without dimmer, e.g. SRF, SLF, etc. Default.
  + dimmer - for module with dimmer, e.g SU, SUF, etc. However, if module supports dimmer, but configured as switch, please use `light` type.
  + rgb_led - for rgb module

* module_mode - module work mode:

  + noolite - for noolite modules, e.g. SU.
  + noolite-f - for noolite-f modules, e.g. SUF, SRF, SLF, etc. Default value.

* scan_interval_value - interval of the module state requests, in seconds. Default value 60 seconds.
* broadcast_value - mode of command sending (affects only **noolite-f** modules):

  + true - send command to all modules in channel simultaneously.
  + false - send command to all modules in channel in serial mode. Default value.

You can see example in `lights.yaml`


Switch
------

Create file `switches.yaml`.

Add next line to `Configuration.yaml`::

    switch: !include switchs.yaml

For each switch add configuration to `switches.yaml`::

    - name: "switch_name"
      platform: noolite
      channel: channel_number
      mode: module_mode
      scan_interval: scan_interval_value
      broadcast: broadcast_value

where

* light_name - name of light, e.g. "hall_light"
* channel_number - channel number on which this sensor was binding
* module_mode - module work mode:

  + noolite - for noolite modules, e.g. SU.
  + noolite-f - for noolite-f modules, e.g. SUF, SRF, SLF, etc. Default value.

* scan_interval_value - interval of the module state requests, in seconds. Default value 60 seconds.
* broadcast_value - mode of command sending (affects only **noolite-f** modules):

  + true - send command to all modules in channel simultaneously.
  + false - send command to all modules in channel in serial mode. Default value.

You can see example in `switches.yaml`


Fan
----

**IMPORTANT!!!** This entity type is experimental.

Create file `fans.yaml`.

Add next line to `Configuration.yaml`::

    fan: !include fans.yaml

For each fan add configuration to `fans.yaml`::

    - name: "fan_name"
      platform: noolite
      channel: channel_number
      mode: module_mode
      speed_enabled: speed_enabled_value
      scan_interval: scan_interval_value
      broadcast: broadcast_value

where

* fan_name - name of fan, e.g. "hall_fan"
* channel_number - channel number on which this sensor was binding
* module_mode - module work mode:

  + noolite - for noolite modules, e.g. SU.
  + noolite-f - for noolite-f modules, e.g. SUF, SRF, SLF, etc. Default value.

* speed_enabled_value - allows speed management:

  + true - speed management is enabled. **Note:** Works only for modules in dimmer mode.
  + false - speed management is disabled. Default value.

* scan_interval_value - interval of the module state requests, in seconds. Default value 60 seconds.
* broadcast_value - mode of command sending (affects only **noolite-f** modules):

  + true - send command to all modules in channel simultaneously.
  + false - send command to all modules in channel in serial mode. Default value.

You can see example in `fans.yaml`


Change log:
==========

v0.1.3
------
* fix work with rgb_led module
* refactor fan component
* update ReadMe

v0.1.2
------
* added manifest.json to match new HomeAssistant requirements
* avoid of using deprecated Light, SwitchDevice and BinarySensorDevice

**Breaking changes:**

* can be don't working with version oldest then 0.108.0

v0.1.1
------
* switch to NooLite-F v0.1.2

v0.1.0
------
* added binary sensors for: door, garage_door, moisture, opening, window, light, motion, battery (in noolite remotes)
* added battery level information

**Breaking changes:**
* platform and type names in config now is in lowercase
* removed unused types
* TempHumi sensor split to two separate sensors: temp and humi
