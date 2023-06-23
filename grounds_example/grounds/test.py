import time
import math
import csv
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plot
import paho.mqtt.client as mqtt

from time import sleep
from datetime import datetime, timedelta
from dotenv import dotenv_values
#from config import PREFIX
from skyfield.api import load, wgs84, Topos, utc
from math import radians, cos, sin, asin, sqrt, atan2, pi, log, log10
from scipy import constants
light = constants.speed_of_light

from ground_config_files.config import *
from ground_config_files.signal import lambda_uplink
#from grounds_example.grounds.satellite.main_constellation import *

distMult = 1e3
freqMult = 1e6

def haversine(grndLNG, grndLAT, satLNG, satLAT):
    
    earthRad = 6371 # km
    
    # grnd = LAT/LNG1, sat = LAT/LNG2 
    grndLNG_rad, grndLAT_rad, satLNG_rad, satLAT_rad = map(np.radians, [grndLNG, grndLAT, satLNG, satLAT])
    
    deltLAT = satLAT_rad - grndLAT_rad
    deltLNG = satLNG_rad - grndLNG_rad
    
    a = sin(deltLAT/2)**2 + cos(grndLAT_rad)*cos(satLAT_rad) * (sin(deltLNG/2)**2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    dist = earthRad * c
    
    return dist


def fspl_nondb(distance, frequency):
    result = ((4 * math.pi * (distance*distMult) * (frequency*freqMult))/(light))**2
    return result

def fspl_db(distance, frequency):
    wave = light / (frequency*freqMult)
    result = 20*log10(distance*distMult) + 20*log10(frequency*freqMult) - 147.55
    return result

def signal_loss(pwr, fspldB):
    result = pwr - fspldB
    return result

def get_length(file_path):
    return 1

def append_data(file_path, distance, free_space):
    fieldnames = ['id', 'distance', 'fspl', 'inView']
    next_id = get_length(file_path)
    with open(file_path, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "id": next_id,
            "distance": distance,
            "fspl": free_space
            })

# name guard used to ensure script only executes if it is run as the __main__
if __name__ == "__main__":
    # Note that these are loaded from a .env file in current working directory
#     credentials = dotenv_values(".env")
#     SMCE_HOST, SMCE_PORT = credentials["SMCE_HOST"], int(credentials["SMCE_PORT"])
#     SMCE_USERNAME, SMCE_PASSWORD = credentials["SMCE_USERNAME"], credentials["SMCE_PASSWORD"]
#     TPC1 = f"{PREFIX}/signals/strength"
#     TPC2 = f"{PREFIX}/signals/satellite_info"
# 
#     CLIENT = mqtt.Client()
#     CLIENT.username_pw_set(username=SMCE_USERNAME, password=SMCE_PASSWORD)
#     CLIENT.tls_set()
#     CLIENT.connect(SMCE_HOST, SMCE_PORT)
#     CLIENT.loop_start
 

    while True:
        eph = load('de421.bsp')
        earth = eph['earth']
        ts = load.timescale()
        now = datetime.utcnow()
        current_time = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
        # 
        # sat_url = 'http://celestrak.org/NORAD/elements/stations.txt'
        # satellites = load.tle_file(sat_url, reload=True)
        # by_name = {sat.name: sat for sat in satellites}
        # satellite = by_name['ISS (ZARYA)']

        sat_url = "https://celestrak.com/NORAD/elements/active.txt"
        satellites = load.tle_file(sat_url)
        by_name = {sat.name: sat for sat in satellites}
        satellite_list = ['ISS (ZARYA)', 'AQUA', 'TERRA', 'SUOMI NPP', 'NOAA 20', 'SENTINEL-2A', 'SENTINEL-2B']

        for name in satellite_list:
            satellite = by_name[name]
            satellite_LAT, satellite_LNG = wgs84.latlon_of(satellite.at(current_time))
            
            satellite_LATdeg = satellite_LAT.degrees
            satellite_LNGdeg = satellite_LNG.degrees
# 
#             alt = wgs84.subpoint(satellite.at(satellite.epoch)).elevation.m
#             min_elev = compute_min_elevation(alt, FIELD_OF_REGARD)
#             sens_radius = compute_sensor_radius(alt, min_elev)
            

            for i, row in GROUND.iterrows():
                groundID = row['groundId']
                lat = row['latitude']
                lng = row['longitude']
                ang = row['elevAngle']
                groundPOS = wgs84.latlon(lat, lng)
#                 inView = check_in_view(current_time, satellite, groundPOS, min_elev)
#                 range = check_in_range(current_time, satellite, GROUND)
#                 min_elev = compute_min_elevation(alt, FIELD_OF_REGARD)
                distance_to_grnd = haversine(lng, lat, satellite_LNGdeg, satellite_LATdeg)
                
                fspl_non = fspl_nondb(distance_to_grnd, uplink)
                fspl_dec = fspl_db(distance_to_grnd, uplink)
                signal_loss_dBW = signal_loss(power, fspl_dec)
                
#                 x = []
#                 y = []
#                 plot.plot(x,y, color='blue', linestyle='dashed', linewidth=3, marker='o',
#                           markersize=6, markerfacecolor='red', markeredgecolor='blue')
                
#                 print("Sat. Name: ", name)
#                 print("satLat: ", satellite_LATdeg, "satLNG: ", satellite_LNGdeg, "ANG: ", min_elev)
#                 print("Zenith Angle: ", get_elevation_angle(current_time, satellite, groundPOS))
#                 print("In View?", inView, "In Range?", range)
#                 print("ID: ", groundID)
#                 print("Lat:", lat, "Long:", lng)
#                 print("Distance: ", haversine(lng, lat, satellite_LNGdeg, satellite_LATdeg))
#                 print("ALT: ", alt)
#                 print()
                print(distance_to_grnd)
                print(fspl_dec)
                
                append_data("data.csv", distance_to_grnd, fspl_dec)
                
#                 satellite_info = (f"DESIGNATOR: {satellite}\n"
#                                  f"GROUND STN #: {groundID}\n"
#                                  f"Latitude/Longitude: {satellite_LATdeg}, {satellite_LNGdeg}\n"
#                                  f"Minimum Viewing Angle: {min_elev}\n" 
#                                  f"Distance to ground station: {distance_to_grnd}"
#                                  f"Satellite in view & in range? {inView},{range}"
#                                   )
#                 if inView and range:
#                     signal_info = (
#                             f"DESIGNATOR: {satellite}\n"
#                             f"FSPL (non-dB): {fspl_non}\n"
#                             f"FSPL (dB): {fspl_dec}\n"
#                             f"Signal loss (dBW): {signal_loss_dBW}"
#                 
#                     )
#                     CLIENT.publish(TPC1, signal_info)
# 
#                 
#                 CLIENT.publish(TPC2, satellite_info)
                
          
           
        #     
        # 
        # alt = wgs84.subpoint(satellite.at(satellite.epoch)).elevation.m
        # min_elev = compute_min_elevation(alt, FIELD_OF_REGARD)
        # sens_radius = compute_sensor_radius(alt, min_elev)
        # range = check_in_range(current_time, satellite, GROUND)
        # 
        # distance_from_grnd = haversine(LNG, LAT, issLNGdeg, issLATdeg)
        # 
        # inView = check_in_view(current_time, satellite, wgs84.latlon(LAT, LNG), min_elev)
        # 



        # print("Altitude: " + "{:.2f}".format(alt) + " m")
        # print("Sensor Radius: " + "{:.2f}".format(sens_radius) + " m")
        # print("In range: ", range)
        # print(issLAT)
        # print(issLNG)
        # print("Distance from ISS to ground station: " + "{:.2f}".format(distance_from_grnd) + " km")
        # print("FSPL (non-dB): " + np.format_float_scientific(fspl_non, 3) + " m^2")
        # print("FSPL (dB): " + np.format_float_scientific(fspl_dec, 3) + " dB")
        # print("Signal loss: " + "{:.2f}".format(signal_loss_dBW) + " dBW")
        # print(min_elev)
        # print(inView)

