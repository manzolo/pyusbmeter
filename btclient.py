import json
import os.path
import time
from datetime import date, timedelta
from os import path

from bluetooth import *

import alert
import datefunction
import sendmail
import websend


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


        dir_path = os.path.dirname(os.path.realpath(__file__))

        d = b""
        filetowrite = dir_path + '/data' + datefunction.nowToDateString() + '.txt'
        myfile = open(filetowrite, 'a')

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

            # g = 0
            # for i in range(16, 95, 8):
            #    ma, mw = struct.unpack(">II", d[i:i + 8])  # mAh,mWh respectively
            #    gs = str(g)
            #    data[gs + '_mAh'] = ma
            #    data[gs + '_mWh'] = mw
            #    g += 1
            #
            # data['data_line_pos_volt'] = struct.unpack(">h", d[96:97 + 1])[0] / 100.0  # data line pos voltage
            # data['data_line_neg_volt'] = struct.unpack(">h", d[98:99 + 1])[0] / 100.0  # data line neg voltage
            # data['resistance'] = struct.unpack(">I", d[122:125 + 1])[0] / 10.0  # resistance

            volts = str(data['Volts'])
            amps = str(data['Amps'])
            watts = str(data['Watts'])
            temps = str(data['temp_C'])
            timestr = datefunction.toDatetimeHrString(data['time'])

            row = timestr + '\t' + volts + '\t' + amps + '\t' + watts + '\t' + temps

            filetowrite = dir_path + '/data' + datefunction.nowToDateString() + '.txt'
            if not path.exists(filetowrite):
                myfile = open(filetowrite, 'a')

            myfile.write("%s\n" % row)
            myfile.flush()

            yesterday = date.today() - timedelta(days=1)
            fileold = dir_path + "/data" + datefunction.toDateString(yesterday) + ".txt"

            if path.exists(fileold):
                sendmail.send()

            if (soglia > 0 and data['Volts'] < soglia):
                alert.send(volts)

            websend.send(addr, timestr, volts, temps)

            # with open('config.json', 'w') as outfile:
            # jsondata["lastvolt"] = volts
            # json.dump(jsondata, outfile)
            d = b""
            sock.send((0xF0).to_bytes(1, byteorder='big'))
            time.sleep(10)

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
