import paho.mqtt.publish as publish
import dotenv
from dotenv import dotenv_values
import RPi.GPIO as GPIO
import time
from time import sleep


credentials = dotenv_values("env")
HOST = credentials["HOST"]
PORT = int(credentials["PORT"])
USERNAME = credentials["USERNAME"]
PASSWORD = credentials["PASSWORD"]

while True:
    publish.single("&hardware/event/LEDBlink", "on", hostname=HOST)
    time.sleep(2)
    publish.single("&hardware/event/LEDBlink", "off", hostname=HOST)
    time.sleep(2)
