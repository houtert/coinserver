import socket
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


def getCurrentTime():
    return datetime.now()


def getCurrentTimeStamp():
    time = datetime.now()
    return convertDateTimeToTimeStamp(time)


def convertDateTimeToString(val):
    return val.strftime(DATETIME_FORMAT)


def convertDateToString(date):
    return date.strftime(DATE_FORMAT)


def convertTimeToString(time):
    return time.strftime(TIME_FORMAT)


def convertStringToDateTime(dateStr):
    return datetime.strptime(dateStr, DATETIME_FORMAT)


def convertDateTimeToTimeStamp(dateTime):
    timestamp = int(datetime.timestamp((dateTime)) * 1000)
    return timestamp


def convertTimeStampToDateTime(timestamp):
    date = datetime.fromtimestamp(timestamp / 1000)
    return date


def convertTimeStampToString(timestamp):
    date = convertTimeStampToDateTime(timestamp)
    return convertDateTimeToString(date)


def getIP():
    return socket.gethostbyname(socket.gethostname())
