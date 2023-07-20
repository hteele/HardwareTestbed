#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:25:21 2023

@author: hteele
"""

import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt

laser_pin = 11

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(laser_pin, GPIO.OUT)
    GPIO.output(laser_pin, GPIO.HIGH)
    
    
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
    TPC = f"{PREFIX}/hrdwr/blinkLED"
    setup()