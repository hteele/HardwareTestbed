# -*- coding: utf-8 -*-
"""
Created on Wed May  3 10:52:20 2023

@author: harry
"""

import paho.mqtt.client as mqtt
import dotenv
from dotenv import dotenv_values
import RPi.GPIO as GPIO
import time
from time import sleep

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

mqtt.Client().enable_logger()

# Note that these are loaded from a .env file in current working directory
credentials = dotenv_values("env")
HOST = credentials["HOST"]
PORT = int(credentials["PORT"])
USERNAME = credentials["USERNAME"]
PASSWORD = credentials["PASSWORD"]
# PREFIX = "&hardware/"

def on_connect(client, userdata, flags, rc):
    print("Connection Established with flags: {flags}, result: {rc}")
    client.subscribe("&hardware/event/LEDBlink")

def on_message(client, userdata, msg):
    print("Message Received, topic: {msg.topic}, message: {msg.payload}")
    if msg.payload.decode() == "on":
        GPIO.output(11, GPIO.HIGH)
    elif msg.payload.decode() == "off":
        GPIO.output(11, GPIO.LOW)

#-----------------------------------------------------
# Launch MQTT

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(HOST, PORT)
client.loop_forever()

