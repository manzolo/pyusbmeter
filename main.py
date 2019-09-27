#!/usr/bin/python3

import json
import time

from bluetooth import *

import btinterface

with open('config.json') as json_data_file:
    data = json.load(json_data_file)

    interfaces = data["interfaces"]
if len(interfaces) == 0:
    nearby_devices = discover_devices()

    for v in nearby_devices:
        print("Found", v)
        interfaces.append(v)
        break

for interface in interfaces:
    print("Try connecting to " + interface)
    if (not interface is None):
        btinterface.connect(interface)
        time.sleep(1)

# crontab -e
# * * * * * cd /home/user/pyusbmeter && /usr/bin/python3 /home/user/pyusbmeter/main.py
# */20 * * * * kill -9 $(ps -eo comm,pid,etimes | awk '/^main.py/ {if ($3 > 660) { print $2}}') 1&>2 /dev/null
