import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

led = Pin(16, Pin.OUT)

wifi_ssid = "Stevens-IoT"
wifi_password = "FSr474fTP3"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

MQTT_SERVER = "192.168.1.174"
#mqtt_username = "" 
#mqtt_password = ""  
MQTT_TPC = "satellite/sunlit/status" 
MQTT_CLIENT = "Pico"

mqtt_client = MQTTClient(client_id=MQTT_CLIENT, server=MQTT_SERVER)

def on_message(topic, msg):
    message = msg.decode("utf-8")
    print (f'Topic {topic} received message {message}')
    if message == 'sunlit':
        print("LED ON")
        led.value(1)
    else:
        print("LED OFF")
        led.value(0)

mqtt_client.set_callback(on_message)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_TPC)
print("Successfully subscribed to the follows topic(s): {MQTT_TPC}")

try:
    while True:
        print(f'Waiting for messages on {MQTT_TPC}')
        mqtt_client.wait_msg()
except Exception as e:
    print(f'Failed to wait for MQTT messages: {e}')
finally:
    mqtt_client.disconnect()