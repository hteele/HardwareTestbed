import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, Topos, utc
from dotenv import dotenv_values
from config import PREFIX

def sunlit_status(satellite, observer, time):
    sunlit = satellite.at(time).is_sunlit(eph)
    return sunlit

eph = load('de421.bsp')
ts = load.timescale()

credentials = dotenv_values(".env")
SMCE_HOST, SMCE_PORT = credentials["SMCE_HOST"], int(credentials["SMCE_PORT"])
SMCE_USERNAME, SMCE_PASSWORD = credentials["SMCE_USERNAME"], credentials["SMCE_PASSWORD"]

# MQTT_SERVER = "192.168.1.174"
# MQTT_TPC1 = "hardware/blinkLED"
TPC = f"{PREFIX}/hrdwr/blinkLED"

sat_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(sat_url)

by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(satellite)


# build the MQTT client
CLIENT = mqtt.Client()
# set client username and password
CLIENT.username_pw_set(username=SMCE_USERNAME, password=SMCE_PASSWORD)
# set tls certificate
CLIENT.tls_set()
# connect to MQTT server on port 8883
CLIENT.connect(SMCE_HOST, SMCE_PORT)
CLIENT.loop_start

# client = mqtt.Client()
# client.connect(MQTT_SERVER, 1883)
# client.loop_start()

observer = Topos(latitude_degrees = 40.744, longitude_degrees = 74.032)

while True:
    now = datetime.utcnow()
    timeS = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
    sunstat = satellite.at(timeS).is_sunlit(eph)

    if sunstat:
        transit_status = "sunlit"
    else:
        transit_status = "in shadow"

    print(timeS.astimezone(utc))

    print("Satellite is", transit_status)
    CLIENT.publish(TPC, transit_status)
    print("Updating in 5 minutes...")
    time.sleep(300)


client.disconnect()
client.loop_stop()
