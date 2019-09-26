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
    try:
        service_matches = find_service(address=addr)

        if len(service_matches) == 0:
            print("No services found for address ", addr)
            return -1

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        print("connecting to \"%s\" on %s" % (name, host))

        sock = BluetoothSocket(RFCOMM)
        res = sock.connect((host, port))

        with open('config.json') as json_data_file:
            jsondata = json.load(json_data_file)

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

            volts = str(data['Volts'])
            amps = str(data['Amps'])
            watts = str(data['Watts'])
            temps = str(data['temp_C'])
            timestr = datefunction.toDatetimeHrString(data['time'])

            if (soglia > 0 and data['Volts'] < soglia):
                alert.send(volts)

            websendnow.send(addr, timestr, volts, temps)

            with open('config.json', 'w') as outfile:
                jsondata["lastvolt"] = volts
                json.dump(jsondata, outfile)

            d = b""
            sock.send((0xF0).to_bytes(1, byteorder='big'))
            sock.close()
            if (myfile is not None):
                myfile.close()

            time.sleep(10)
            return -100

    except Exception as e:
        print(e)
        try:
            sock.close()
            if (myfile is not None):
                myfile.close()
            return -2
        except Exception as e:
            print(addr + " disconnect")
            # print(e)
            return -3
        finally:
            print(addr + " disconnect")
