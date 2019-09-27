import json
import time
from bluetooth import *
import alert
import datefunction
import websendnow

import bluetooth
import struct
import time


def connect_to_usb_tester(bt_addr):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((bt_addr, 1))
        sock.settimeout(1.0)
        for _ in range(10):
            try:
                read_data(sock)
            except bluetooth.BluetoothError as e:
                time.sleep(0.2)
            else:
                break
        return sock

    except Exception as e:
        print(e)

def read_data(sock):
    sock.send(bytes([0xF0]))
    d = bytes()
    while len(d) < 130:
        d += sock.recv(1024)
    assert len(d) == 130, len(d)
    return d


def read_measurements(sock):
    d = read_data(sock)
    assert d[0:2] == bytes([0x09, 0x63])
    assert d[-2:] == bytes([0xff, 0xf1])
    voltage, current, power = [x / 100 for x in struct.unpack('!HHI', d[2:10])]
    temp_celsius, temp_fahrenheit = struct.unpack('!HH', d[10:14])
    usb_data_pos_voltage, usb_data_neg_voltage = [x / 100 for x in struct.unpack('!HH', d[96:100])]
    charging_mode = d[100]
    del d
    del sock
    return locals()


def connect(bt_addr):
    try:
        sock = connect_to_usb_tester(bt_addr)
        try:
            measurement = read_measurements(sock)
            volt = measurement["voltage"]
            temps = measurement["temp_celsius"]
            checkthreshold(bt_addr, volt)
            websendnow.send(bt_addr, datefunction.nowToDatetimeHrString(), volt, temps)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
    finally:
        if not sock is None:
            sock.close()


def checkthreshold(bt_addr, volt):
    soglia = 0
    with open('config.json') as json_data_file:
        jsondata = json.load(json_data_file)
    soglia = jsondata["voltthreshold"]
    if (soglia > 0 and volt < soglia):
        alert.send(bt_addr, volt)



# def connect(addr):
#     myfile = None
#     sock = None
#     soglia = 0
#     service_matches = find_service(address=addr)
#
#     if len(service_matches) == 0:
#         print("No services found for address ", addr)
#         return -1
#
#     first_match = service_matches[0]
#     port = first_match["port"]
#     name = first_match["name"]
#     host = first_match["host"]
#
#     if name is None:
#         print("Error retrieve information address ", addr)
#         return -2
#
#     print("connecting to %s \"%s\" on %s" % (name, host, port))
#
#     try:
#         with open('config.json') as json_data_file:
#             jsondata = json.load(json_data_file)
#
#         sock = BluetoothSocket(RFCOMM)
#         res = sock.connect((host, port))
#
#         soglia = jsondata["voltthreshold"]
#
#         leng = 20
#
#         sock.send((0xF0).to_bytes(1, byteorder='big'))
#
#         d = b""
#
#         print("connected to \"%s\" on %s" % (name, host))
#
#         while True:
#             d += sock.recv(130)
#
#             if len(d) != 130:
#                 continue
#
#             data = {}
#
#             data['Volts'] = struct.unpack(">h", d[2:3 + 1])[0] / 100.0  # volts
#             data['Amps'] = struct.unpack(">h", d[4:5 + 1])[0] / 1000.0  # amps
#             data['Watts'] = struct.unpack(">I", d[6:9 + 1])[0] / 1000.0  # watts
#             data['temp_C'] = struct.unpack(">h", d[10:11 + 1])[0]  # temp in C
#             # data['temp_F'] = struct.unpack(">h", d[12:13 + 1])[0]  # temp in F
#
#             data['time'] = datefunction.now()
#
#             volts = data['Volts']
#             amps = data['Amps']
#             watts = data['Watts']
#             temps = data['temp_C']
#             timestr = datefunction.toDatetimeHrString(data['time'])
#
#             if (soglia > 0 and data['Volts'] < soglia):
#                 alert.send(addr, volts)
#
#             websendnow.send(addr, timestr, volts, temps)
#
#             d = b""
#             sock.send((0xF0).to_bytes(1, byteorder='big'))
#             time.sleep(1)
#             sock.close()
#             if (myfile is not None):
#                 myfile.close()
#             return 0
#
#     except Exception as e:
#         print(e)
#         try:
#             sock.close()
#             if (myfile is not None):
#                 myfile.close()
#             return -2
#         except Exception as e:
#             print(addr + " disconnect")
#             return -3
#         finally:
#             print(addr + " disconnect")
