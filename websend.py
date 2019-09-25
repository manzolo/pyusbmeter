import json
from datetime import datetime

import requests

import datefunction


def send(device, datalog, volt, temp):
    try:
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)

        if (len(data["lastwebsenddate"]) == 0):
            realsend(device, datalog, volt, temp)
            data["lastwebsenddate"] = datefunction.nowToDatetimeHrString()
            with open('config.json', 'w') as outfile:
                json.dump(data, outfile)

        else:
            lastcheck = datetime.strptime(data["lastwebsenddate"], '%Y-%m-%d %H:%M:%S')
            time = ((datefunction.now().replace(tzinfo=None) - lastcheck).total_seconds())
            # print(time)

            if (time > 60 * 30):
                realsend(device, datalog, volt, temp)
    except Exception as e:
        print(e)


def realsend(device, datalog, volt, temp):
    try:
        with open('config.json') as json_data_file:
            data = json.load(json_data_file)

            datasend = {"device": device, 'data': datalog, 'volt': volt, 'temp': temp}
            data_json = json.dumps(datasend)
            payload = {'data': data_json}
            r = requests.post(data["webserver"] + '/api/sendvolt', data=payload)

            # print(r.status_code)
            # print(r.json())
            data["lastwebsenddate"] = datefunction.nowToDatetimeHrString()
            with open('config.json', 'w') as outfile:
                json.dump(data, outfile)
    except Exception as e:
        print(e)
