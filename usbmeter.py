#!/usr/bin/python3

import argparse
import time

from bluetooth import *

import btclient

parser = argparse.ArgumentParser(description="CLI for USB Meter")
parser.add_argument("--addr", dest="addr", type=str, help="Address of USB Meter")

args = parser.parse_args()
addr = None

if args.addr:
    addr = args.addr
else:
    nearby_devices = discover_devices(lookup_names=True)

    for v in nearby_devices:
        if v[1] == "UM25C":
            print("Found", v[0])
            addr = v[0]
            break

while True:
    if (btclient.connect(addr) == -100):
        quit(0)

    time.sleep(10)
