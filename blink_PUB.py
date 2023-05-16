import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from time import sleep

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

MQTT_SERVER = "192.168.1.174"
MQTT_TPC = "hardware/blinkLED"

def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))
    client.subscribe(MQTT_TPC)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode("utf-8")
    if message == "on":
        GPIO.output(11, GPIO.HIGH)
    if message == "off":
        GPIO.output(11, GPIO.LOW)
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883)
client.loop_forever()