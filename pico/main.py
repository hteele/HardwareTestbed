import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
from wificonfig import *

standby = Pin("LED", Pin.OUT)
led = Pin(16, Pin.OUT)

def on_message(TPC, msg):
    message = msg.decode("utf-8")
    topic = TPC.decode("utf-8")
    print (f'Topic {topic} received message: {message}')
    if message == 'sunlit':
        print("LED ON")
        led.value(1)
    else:
        print("LED OFF")
        led.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

if wlan.isconnected == False:
    sleep(1)

print("Successfully Connected to " + ssid)
TPC = f"{PREFIX}/hrdwr/blinkLED"
PICOCLIENT = "Pico"

CLIENT = MQTTClient(client_id=PICOCLIENT, server=SMCE_HOST, port=SMCE_PORT, user=SMCE_USERNAME, password=SMCE_PASSWORD, ssl=True)

CLIENT.set_callback(on_message)
CLIENT.connect()
print("Connected to {SMCE_HOST}")
CLIENT.subscribe(TPC)
print("Successfully subscribed to the follows topic(s): {TPC}")
# Onboard LED static if successfully connected
standby.on()

try:
    while True:
        print(f'Waiting for messages on {TPC}')
        CLIENT.wait_msg()
except Exception as e:
    print(f'Failed to wait for MQTT messages: {e}')
    # Flash onboard LED if connection failed
    while True:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)
finally:
    CLIENT.disconnect()