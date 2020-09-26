#!/usr/bin/python3
# ups-mqtt.py

import os
import subprocess
import paho.mqtt.publish as mqtt
import time
from time import sleep, localtime, strftime
import datetime
from configparser import ConfigParser
import shutil
import json

if not os.path.exists('conf/config.ini'):
    shutil.copy('config.ini', 'conf/config.ini')

# Load configuration file
config_dir = os.path.join(os.getcwd(), 'conf/config.ini')
config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
config.optionxform = str
config.read(config_dir)

base_topic = config['MQTT'].get('base_topic', 'home/ups')
if not base_topic.endswith('/'):
    base_topic += '/'

ups_host = config['UPS'].get('hostname', 'localhost')
ups_name = config['UPS'].get('ups_name', 'ups')
mqtt_host = config['MQTT'].get('hostname', 'localhost')
mqtt_port = config['MQTT'].getint('port', 1883)
mqtt_user = config['MQTT'].get('username', None)
mqtt_password = config['MQTT'].get('password', None)
interval = config['General'].getint('interval', 60)
ups_serial_number_field = config['UPS'].get('ups_serial_number_field', 'ups.serial')
ups_input_voltage_field = config['UPS'].get('ups_serial_number_field', 'input.voltage')
ups_id = "";

def get_ups_infomation():
    ups = subprocess.run(["upsc", ups_name  + "@" + ups_host], stdout=subprocess.PIPE)
    lines = ups.stdout.decode('utf-8').split('\n')
    json_dict = {}
    for line in lines:
        fields = line.split(':')
        if len(fields) < 2:
            continue
        key = fields[0].strip()
        value = fields[1].strip()
        json_dict[key] = value

    print(json.dumps(json_dict))

    print(json_dict[ups_serial_number_field])
    global ups_id
    ups_id = json_dict[ups_serial_number_field]

def setup_home_assistant():

    voltage_payload = {"name": ups_id + " UPS Line Voltage", "state_topic": "homeassistant/sensor/" + ups_id + "/state","platform": "mqtt", "value_template": "{{ value_json['" + ups_input_voltage_field + "']}}" }
    mqtt.single(topic="homeassistant/sensor/" + ups_id + "VIN/config", payload=json.dumps(voltage_payload), hostname=mqtt_host, port=mqtt_port, auth={'username': mqtt_user, 'password': mqtt_password})


def process():
    topic = "homeassistant/sensor/" + ups_id + "/state"
    ups = subprocess.run(["upsc", ups_name  + "@" + ups_host], stdout=subprocess.PIPE)
    lines = ups.stdout.decode('utf-8').split('\n')

    json_dict = {}
    for line in lines:
        fields = line.split(':')
        if len(fields) < 2:
            continue
        key = fields[0].strip()
        value = fields[1].strip()
        json_dict[key] = value
    mqtt.single(topic, payload=json.dumps(json_dict), hostname=mqtt_host, port=mqtt_port, auth={'username': mqtt_user, 'password': mqtt_password})



while True:
    get_ups_infomation()
    setup_home_assistant()
    process()
    sleep(interval)
