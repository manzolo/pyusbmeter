import json

import requests

import datefunction


def send(device, datalog, volt, temp):
    try:
        try:
            with open('config.json') as json_data_file:
                data = json.load(json_data_file)

                datasend = {"device": device, 'data': datalog, 'volt': volt, 'temp': temp}
                data_json = json.dumps(datasend)
                payload = {'data': data_json}
                r = requests.post(data["webserver"] + '/api/sendvolt', data=payload)

                # print(r.status_code)
                # print(r.json())
                data[device]["lastwebsenddate"] = datefunction.nowToDatetimeHrString()
                data[device]["lastvolt"] = volt

                with open('config.json', 'w') as outfile:
                    json.dump(data, outfile)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
