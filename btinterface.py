import json
import time

from bluetooth import *

import alert
import datefunction
import websendnow


def connect(addr):
    myfile = None
    sock = None
    soglia = 0
    service_matches = find_service(address=addr)

    if len(service_matches) == 0:
        print("No services found for address ", addr)
        return -1

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    if name is None:
        print("Error retrieve information address ", addr)
        return -2

    print("connecting to %s \"%s\" on %s" % (name, host, port))

    try:
        with open('config.json') as json_data_file:
            jsondata = json.load(json_data_file)

        sock = BluetoothSocket(RFCOMM)
        res = sock.connect((host, port))

        soglia = jsondata["voltthreshold"]

        leng = 20

        sock.send((0xF0).to_bytes(1, byteorder='big'))

        d = b""

        print("connected to \"%s\" on %s" % (name, host))

        while True:
            d += sock.recv(130)

            if len(d) != 130:
                continue

            data = {}

            data['Volts'] = struct.unpack(">h", d[2:3 + 1])[0] / 100.0  # volts
            data['Amps'] = struct.unpack(">h", d[4:5 + 1])[0] / 1000.0  # amps
            data['Watts'] = struct.unpack(">I", d[6:9 + 1])[0] / 1000.0  # watts
            data['temp_C'] = struct.unpack(">h", d[10:11 + 1])[0]  # temp in C
            # data['temp_F'] = struct.unpack(">h", d[12:13 + 1])[0]  # temp in F

            data['time'] = datefunction.now()

            volts = data['Volts']
            amps = data['Amps']
            watts = data['Watts']
            temps = data['temp_C']
            timestr = datefunction.toDatetimeHrString(data['time'])

            if (soglia > 0 and data['Volts'] < soglia):
                alert.send(addr, volts)

            websendnow.send(addr, timestr, volts, temps)

            d = b""
            sock.send((0xF0).to_bytes(1, byteorder='big'))
            time.sleep(1)
            sock.close()
            if (myfile is not None):
                myfile.close()
            return 0

    except Exception as e:
        print(e)
        try:
            sock.close()
            if (myfile is not None):
                myfile.close()
            return -2
        except Exception as e:
            print(addr + " disconnect")
            return -3
        finally:
            print(addr + " disconnect")
