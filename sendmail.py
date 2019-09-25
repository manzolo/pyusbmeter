#!/usr/bin/python3
import datetime
import json
import os.path
import smtplib
from datetime import date
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path


def send():
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)

        smtphost = data["mailserver"]["host"]
        smtpport = data["mailserver"]["port"]
        smtpuser = data["mailserver"]["user"]
        smtppwd = data["mailserver"]["passwd"]

        send_to_email = data["mailserver"]["sendto"]

        subject = 'Bt Datalogger'
        message = 'Have a nice day'

        dir_path = os.path.dirname(os.path.realpath(__file__))

        for day in range(30):
            if day == 0:
                continue

            yesterday = date.today() - datetime.timedelta(days=day)
            file_location = dir_path + "/data" + yesterday.strftime('%Y-%m-%d') + ".txt"

            if (not path.exists(file_location)):
                print(file_location + ' not found')
                continue

            msg = MIMEMultipart()
            msg['From'] = smtpuser
            msg['To'] = send_to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            # Setup the attachment
            filename = os.path.basename(file_location)
            attachment = open(file_location, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            # Attach the attachment to the MIMEMultipart object
            msg.attach(part)

            try:
                server = smtplib.SMTP(smtphost, smtpport)
                server.login(smtpuser, smtppwd)
                text = msg.as_string()
                server.sendmail(smtpuser, send_to_email, text)
                server.quit()
                print("Successfully sent email")
                os.rename(file_location, file_location + '.bak')
            except Exception as e:
                print("Error: unable to send email")
                print(e)
