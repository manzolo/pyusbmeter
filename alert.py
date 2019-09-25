#!/usr/bin/python3
import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open('config.json') as json_data_file:
    data = json.load(json_data_file)

    smtphost = data["mailserver"]["host"]
    smtpport = data["mailserver"]["port"]
    smtpuser = data["mailserver"]["user"]
    smtppwd = data["mailserver"]["passwd"]

    send_to_email = data["mailserver"]["sendto"]

    subject = 'WARNING, LOW BATTERY LEVEL !!!'

    message = sys.argv[1] + ' Volt'

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
    except:
        print("Error: unable to send email")
