#!/usr/bin/python3

import json
import time

from bluetooth import *

import btsend

addr = None

with open('config.json') as json_data_file:
    data = json.load(json_data_file)

interface = data["interface"]
if len(interface) > 0:
    print("Device loaded from config -> " + interface)
    addr = interface
else:
    nearby_devices = discover_devices(lookup_names=True)

    for v in nearby_devices:
        if v[1] == data["devicename"]:
            print("Found", v[0])
            addr = v[0]
            break

while True:
    if (not addr is None):
        if (btsend.connect(addr) == -100):
            quit(0)

    time.sleep(10)

# crontab -e
# * * * * * cd /home/user/pyusbmeter && /usr/bin/python3 /home/user/pyusbmeter/main.py
