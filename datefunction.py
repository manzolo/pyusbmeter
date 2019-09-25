#!/usr/bin/python3
import datetime


def now():
    utc_dt = datetime.datetime.now(datetime.timezone.utc)  # UTC time
    return utc_dt.astimezone()  # local time


def toDatetimeString(date):
    return date.strftime("%Y-%m-%d_%H:%M:%S")


def toDatetimeHrString(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")


def toDateString(date):
    return date.strftime("%Y-%m-%d")


def nowToDateString():
    return now().strftime("%Y-%m-%d")


def nowToDatetimeString():
    return now().strftime("%Y-%m-%d_%H:%M:%S")


def nowToDatetimeHrString():
    return now().strftime("%Y-%m-%d %H:%M:%S")
