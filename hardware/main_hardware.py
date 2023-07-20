#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:25:21 2023

@author: hteele
"""

import RPi.GPIO as GPIO
import time
from time import sleep
import json
from dotenv import dotenv_values
import paho.mqtt.client as mqtt
from config import (
    PREFIX,
    TPC
    )

laser_pin = 11
json_data = None

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(laser_pin, GPIO.OUT)
    GPIO.output(laser_pin, GPIO.LOW)
    
def on_connect(CLIENT, userdata, flags, rc):
    CLIENT.subscribe(TPC)
        
def on_message(CLIENT, userdata, msg):
    global json_data
    comm_range = json_data.get("commRange")
    
    if comm_range:
        GPIO.output(laser_pin, GPIO.HIGH)
        print("Laser emitted")
    else:
        GPIO.output(laser_pin, GPIO.LOW)
    
def mqtt_init():
    CLIENT = mqtt.Client()
    CLIENT.username_pw_set(username=USERNAME, password=PASSWORD)
    CLIENT.tls_set()
    CLIENT.on_connect = on_connect
    CLIENT.on_message = on_message
    CLIENT.connect(HOST,PORT)
    print(f"Successfully connected to {HOST} on topic(s) {TPC}")
    CLIENT.loop_forever()
    
    
def loop():
    while True:
        GPIO.output(laser_pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(laser_pin, GPIO.HIGH)
        time.sleep(0.5)
        
def destroy():
    GPIO.OUTPUT(laser_pin, GPIO.HIGH)
    GPIO.cleanup()
    

if __name__ == '__main__':
    credentials = dotenv_values(".env")
    HOST, PORT = credentials["HOST"], int(credentials["PORT"])
    USERNAME, PASSWORD = credentials["USERNAME"], credentials["PASSWORD"]
    setup()
    mqtt_init()
    