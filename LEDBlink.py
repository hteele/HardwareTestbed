# -*- coding: utf-8 -*-
"""
Created on Wed May  3 10:52:20 2023

@author: harry
"""

import pahot.mqtt.client as mqtt
import dotenv as env

# Note that these are loaded from a .env file in current working directory
credentials = env(".env")
HOST, PORT = credentials["HOST"], int(credentials["PORT"])
USERNAME, PASSWORD = credentials["USERNAME"], credentials["PASSWORD"]
PREFIX = "&hardware/"

def on_connect(client, userdata, flags, rc):
    print("Connection Established with flags: {flags}, result: {rc}")
    client.subscribe("{PREFIX}/event/LEDBlink")
    return

def on_message(client, userdata, msg):
    print("Message Received, topic: {msg.topic}, message: {msg.payload}")
    return    

#-----------------------------------------------------
# Launch MQTT

client = mqtt.Client()
client.connect(HOST, PORT)
client.enable_logger()
client.on_connect = on_connect
client.on_message = on_message 
client.loop_forever()

