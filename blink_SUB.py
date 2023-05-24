import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, Topos, utc

def sunlit_status(satellite, observer, time):
    sunlit = satellite.at(time).is_sunlit(eph)
    return sunlit

eph = load('de421.bsp')
ts = load.timescale()

MQTT_SERVER = "192.168.1.174"
MQTT_TPC1 = "hardware/blinkLED"
MQTT_TPC2 = "satellite/sunlit/status"

sat_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(sat_url)

by_name = {sat.name: sat for sat in satellites}
satellite = by_name['ISS (ZARYA)']
print(satellite)

client = mqtt.Client()
client.connect(MQTT_SERVER, 1883)
client.loop_start()

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
    client.publish(MQTT_TPC2, transit_status)
    print("Updating in 5 minutes...")
    time.sleep(300)


client.disconnect()
client.loop_stop()
