#!/usr/bin/python3
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datefunction


def send(addr, volt):
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)

    lastvolt = data[addr]["lastvolt"]
    if len(data[addr]["lastalertdate"]) > 0:
        lastcheck = datetime.strptime(data[addr]["lastalertdate"], '%Y-%m-%d %H:%M:%S')
        if (((datefunction.now().replace(tzinfo=None) - lastcheck).total_seconds()) < 3600):
            print("Already: " +str(((datefunction.now().replace(tzinfo=None) - lastcheck).total_seconds())))
            return

    print("Last:" + str(lastvolt))
    print("Curr:" + str(volt))
    print("Diff:" + str(lastvolt - volt))
    #
    if lastvolt <= 0:
        print("No rif.")
        return

    #if volt >= lastvolt:
    #    print("Up")
    #    return


    smtphost = data["mailserver"]["host"]
    smtpport = data["mailserver"]["port"]
    smtpuser = data["mailserver"]["user"]
    smtppwd = data["mailserver"]["passwd"]

    send_to_email = data["mailserver"]["sendto"]

    message = addr + ' detected ' + str(volt) + ' volt, previous value ' + str(lastvolt) + ' volt'

    subject = 'WARNING, LOW BATTERY LEVEL ' + str(volt) + ' Volt on ' + addr + '!!!'

    msg = MIMEMultipart()
    msg['From'] = smtpuser
    msg['To'] = send_to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtphost, smtpport)
        server.login(smtpuser, smtppwd)
        text = msg.as_string()
        server.sendmail(smtpuser, send_to_email, text)
        server.quit()
        print("Successfully sent email")
        data[addr]["lastalertdate"] = datefunction.nowToDatetimeHrString()
        data[addr]["lastvolt"] = volt

        with open('config.json', 'w') as outfile:
            json.dump(data, outfile)
    except:
        print("Error: unable to send email")
