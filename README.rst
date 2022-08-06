HomeAssistance-NooLite
======================

NooLite platform for Home Assistance

**Note:** Currently supported only MTRF adapters.

**Note:** version 0.1.+ supported only in HA 8.16.0 and above. It is related to changing of the custom component architecture.
**Note:** version 0.2.+ supported only in HA 2022.2.2 and above.

Installation
============

* Copy `custom_components` folder from this repo into your Home Assistant config folder.


Platform configuration
======================

Add next rows to `Configuration.yaml`::

    noolite:
      port: "port_name"
      baudrate: baudrate_value

where `port_name` is your NooLite adapter port:

* for Windows it is `COM0`, `COM1`, etc.
* fot Linux it is `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

and `baudrate_value` is port baudrate:

* 9600 (default value)
* 115200 (requires upgrade MTRF adapter firmware)


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
  + remote (for noolite remotes, support on, off and switch events)

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
  + remote - noolite remotes
  + rgb_remote - noolite rgb remotes

You can see example in file `sensors.yaml`

Possible states for `remote` sensor type:

+ on
+ off
+ switch
+ tune_up
+ tune_down
+ tune_back
+ tune_stop
+ load_preset
+ save_preset

Possible states for `rgb_remote` sensor type:

+ switch
+ tune_back
+ tune_stop
+ roll_color
+ switch_mode
+ switch_color
+ switch_speed

Each of these states match to appropriate command received from remote. For more details see manual for remotes.

**Note:** Each state stay active around 200ms, after this it reset to `unknown` value. It is related to that noolite remotes send commands not states.

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


Services
========

Noolite integration extends default services for lights, fans and switch.

**IMPORTANT** using some services with modules in `noolite` mode, can cause incorrect states.
It is related that we don known finish state after service call. For example, service noolite.light_load_preset
restores saved state, but we don't know which this state is: on or off, which brightness was saved.

Lights
------

Allowing following services:

* noolite.light_start_brightness_tune - start brightness changing in specific direction (only for dimmer type)
* noolite.light_stop_brightness_tune - stop brightness changing (only for dimmer type)
* noolite.light_load_preset - load and apply saved module tate (temporary only for dimmer type)
* noolite.light_save_preset - save current module state (temporary available only for dimmer type)
* noolite.rgb_start_brightness_tune - start brightness changing in specific direction (only available for rgb_led type)
* noolite.rgb_stop_tune - stop brightness changing (only for rgb_led type)
* noolite.rgb_start_roll_color - start color changing (only for rgb_led type)
* noolite.rgb_switch_color - switch color to next (only for rgb_led type)
* noolite.rgb_switch_mode - switch controller work mode: fixed color or change colors (only for rgb_led type)
* noolite.rgb_start_switch_speed - start speed changing of color switching (only for rgb_led type)
* noolite.rgb_load_preset - load and apply saved module tate (temporary available only for rgb_led type)
* noolite.rgb_save_preset - save current module state (temporary available only for rgb_led type)


Switches
--------

Allowing following services:

* noolite.switch_load_preset - load and apply saved module tate
* noolite.switch_save_preset - save current module state

Fans
----

Allowing following services:

* noolite.fan_start_speed_tune - start speed changing in specific direction (only if fan uses noolite-f module and speed_enabled is set to true)
* noolite.fan_stop_speed_tune - stop speed changing (only if fan uses noolite-f module and speed_enabled is set to true)
* noolite.fan_load_preset - load and apply saved module tate (temporary available only if fan uses noolite-f module and speed_enabled is set to true)
* noolite.fan_save_preset - save current module state (temporary available only if fan uses noolite-f module and speed_enabled is set to true)

Bind noolite remotes with services
----------------------------------

Create file `automations.yaml`.

Add next line to `Configuration.yaml`::

    automation: !include automations.yaml

After this you can create automations using HA interface. Open HA in browser, go to Configurations -> Automations and scenes.
Also you can create automations manually. Please see parameters required for services in examples in automations.yaml.


Change log:
==========
v0.2.2
------
* return switch event handling for binary sensors

v0.2.1
------
* add possibility to set port baudrate

v0.2.0
------
* reworking binary_sensors and sensors for noolite remotes
* add rgb remote support
* update sensors to subclass of SensorEntity
* use attributes instead of override methods
* add noolite service that allows use native module command

**Breaking changes:**

* can be don't working with version oldest then 2022.2.2
* rename remote sensor states, so old sensor config can be broken

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
