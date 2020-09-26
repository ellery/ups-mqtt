# ups-mqtt

Based off of the work of [dniklewicz](https://github.com/dniklewicz).

Simple python tool for fetching data from NUT server and publishing output to MQTT server.\
Can be used for UPS connected to Synology NAS with UPS Network Server Enabled.

Example included for passing values to Home Assistant via MQTT, auto discovery coming soon

Configuration via file `/opt/app/conf/config.ini`.\
If used with Synology UPS Network Server, please remember to add container's IP address to the whitelist.

## Default configuration file:
```
[UPS]
# Address of NUT server
#hostname=localhost

[MQTT]
# Base MQTT topic
#base_topic=home/ups

# Address of MQTT server
#hostname=localhost

# MQTT server port
#port=1883

# MQTT username
#username=

# MQTT password
#password=

[General]
# Polling interval in seconds
#interval=60
```

## Networking
If you want to get the same IP address for your docker container between restarts, you can create new docker network with limited address space:
```
Subnet mask: 172.xx.0.0/30
IP range: 172.xx.0.0/30
Gateway: 172.xx.0.1
```
Then your container should use address `172.xx.0.2`.

Use at your own risk. No warranty provided.

## Home Assistant Example


```
sensor:
  - platform: mqtt
    name: "UPS Voltage"
    state_topic: "home/ups/payload"
    unit_of_measurement: 'Volts'
    value_template: "{{  value_json['input.voltage'] }}"
  - platform: mqtt
    name: "UPS Load"
    state_topic: "home/ups/payload"
    unit_of_measurement: '%'
    value_template: "{{  value_json['ups.load'] }}"
  - platform: mqtt
    name: "UPS Battery Voltage"
    state_topic: "home/ups/payload"
    unit_of_measurement: 'Volts'
    value_template: "{{  value_json['battery.voltage'] }}"
  - platform: mqtt
    name: "Battery Charge"
    state_topic: "home/ups/payload"
    unit_of_measurement: '%'
    value_template: "{{  value_json['battery.charge'] }}"
  - platform: mqtt
```
