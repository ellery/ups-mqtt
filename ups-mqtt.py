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

def process():
    ups = subprocess.run(["upsc", ups_name  + "@" + ups_host], stdout=subprocess.PIPE)
    lines = ups.stdout.decode('utf-8').split('\n')

    msgs = []
    json_dict = {}
    for line in lines:
        fields = line.split(':')
        if len(fields) < 2:
            continue
        key = fields[0].strip()
        value = fields[1].strip()
        json_dict[key] = value
        msgs.append((base_topic + key, value, 0, True))
    mqtt.single(base_topic + 'payload', payload=json.dumps(json_dict), hostname=mqtt_host, port=mqtt_port, auth={'username': mqtt_user, 'password': mqtt_password})



while True:
    process()
    sleep(interval)
