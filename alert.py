#!/usr/bin/python3
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datefunction


def send(volt):
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)

        lastvolt = data["lastvolt"]
        lastcheck = datetime.strptime(data["lastalertdate"], '%Y-%m-%d %H:%M:%S')
        #print(str(float(lastvolt)-float(volt)))
        if float(lastvolt) <= 0 or (float(lastvolt) > float(volt) and (float(lastvolt) - float(volt) < 0.05)):
            print(str("Volt " + lastvolt + " -> " + volt))
        else:
            # if (((datefunction.now().replace(tzinfo=None) - lastcheck).total_seconds()) < 60 * 60):
            #   return

            smtphost = data["mailserver"]["host"]
            smtpport = data["mailserver"]["port"]
            smtpuser = data["mailserver"]["user"]
            smtppwd = data["mailserver"]["passwd"]

            send_to_email = data["mailserver"]["sendto"]

            message = 'Detected ' + volt + ' volt, previous value ' + lastvolt + ' volt'

            subject = 'WARNING, LOW BATTERY LEVEL ' + volt + ' Volt' + '!!!'

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
                data["lastalertdate"] = datefunction.nowToDatetimeHrString()
                data["lastvolt"] = volt
                with open('config.json', 'w') as outfile:
                    json.dump(data, outfile)
            except:
                print("Error: unable to send email")
