import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from time import sleep

# Mosquitto Publish: mosquitto_pub -h localhost -t "TOPIC" -m "MESSAGE"
# Mosquitto Subscribe: mosquitto_sub -h localhost -t "TOPIC"

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

MQTT_SERVER = "192.168.1.174"
MQTT_TPC = "satellite/sunlit/status"

def on_connect(client, userdata, flags, rc):
    print("Connected with code " + str(rc))
    client.subscribe(MQTT_TPC)
    print("Connected to the following topics: " + MQTT_TPC)

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode("utf-8")
    if msg.topic == MQTT_TPC and message == "sunlit":
        GPIO.output(11, GPIO.HIGH)
        print("ISS is sunlit")
    else:
        GPIO.output(11, GPIO.LOW)
        print("ISS is in shadow")
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883)
client.loop_forever()
