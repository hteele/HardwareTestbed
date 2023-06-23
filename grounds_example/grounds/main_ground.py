import time
import math
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


def compute_min_elevation(altitude, field_of_regard):
    """
    Computes the minimum elevation angle required for a satellite to observe a point from current location.

    Args:
        altitude (float): Altitude (meters) above surface of the observation
        field_of_regard (float): Angular width (degrees) of observation

    Returns:
        float : min_elevation
            The minimum elevation angle (degrees) for observation
    """
    earth_equatorial_radius = 6378137.000000000
    earth_polar_radius = 6356752.314245179
    earth_mean_radius = (2 * earth_equatorial_radius + earth_polar_radius) / 3

    # eta is the angular radius of the region viewable by the satellite
    sin_eta = np.sin(np.radians(field_of_regard / 2))
    # rho is the angular radius of the earth viewed by the satellite
    sin_rho = earth_mean_radius / (earth_mean_radius + altitude)
    # epsilon is the min satellite elevation for obs (grazing angle)
    cos_epsilon = sin_eta / sin_rho
    if cos_epsilon > 1:
        return 0.0
    return np.degrees(np.arccos(cos_epsilon))


def compute_sensor_radius(altitude, min_elevation):
    """
    Computes the sensor radius for a satellite at current altitude given minimum elevation constraints.

    Args:
        altitude (float): Altitude (meters) above surface of the observation
        min_elevation (float): Minimum angle (degrees) with horizon for visibility

    Returns:
        float : sensor_radius
            The radius (meters) of the nadir pointing sensors circular view of observation
    """
    earth_equatorial_radius = 6378137.0
    earth_polar_radius = 6356752.314245179
    earth_mean_radius = (2 * earth_equatorial_radius + earth_polar_radius) / 3
    # rho is the angular radius of the earth viewed by the satellite
    sin_rho = earth_mean_radius / (earth_mean_radius + altitude)
    # eta is the nadir angle between the sub-satellite direction and the target location on the surface
    eta = np.degrees(np.arcsin(np.cos(np.radians(min_elevation)) * sin_rho))
    # calculate swath width half angle from trigonometry
    sw_HalfAngle = 90 - eta - min_elevation
    if sw_HalfAngle < 0.0:
        return 0.0
    return earth_mean_radius * np.radians(sw_HalfAngle)


def get_elevation_angle(t, sat, loc):
    """
    Returns the elevation angle (degrees) of satellite with respect to the topocentric horizon.

    Args:
        t (:obj:`Time`): Time object of skyfield.timelib module
        sat (:obj:`EarthSatellite`): Skyview EarthSatellite object from skyfield.sgp4lib module
        loc (:obj:`GeographicPosition`): Geographic location on surface specified by latitude-longitude from skyfield.toposlib module

    Returns:
        float : alt.degrees
            Elevation angle (degrees) of satellite with respect to the topocentric horizon
    """
    difference = sat - loc
    topocentric = difference.at(t)
    # NOTE: Topos uses term altitude for what we are referring to as elevation
    alt, az, distance = topocentric.altaz()
    return alt.degrees


def check_in_view(t, satellite, topos, min_elevation):
    """
    Checks if the elevation angle of the satellite with respect to the ground location is greater than the minimum elevation angle constraint.

    Args:
        t (:obj:`Time`): Time object of skyfield.timelib module
        satellite (:obj:`EarthSatellite`): Skyview EarthSatellite object from skyfield.sgp4lib module
        topos (:obj:`GeographicPosition`): Geographic location on surface specified by latitude-longitude from skyfield.toposlib module
        min_elevation (float): Minimum elevation angle (degrees) for ground to be in view of satellite, as calculated by compute_min_elevation

    Returns:
        bool : isInView
            True/False indicating visibility of ground location to satellite
    """
    isInView = False
    horz_elev = get_elevation_angle(t, satellite, topos)
    if horz_elev >= min_elevation:
        isInView = True
    return isInView


def check_in_range(t, satellite, grounds):
    """
    Checks if the satellite is in range of any of the operational ground stations.

    Args:
        t (:obj:`Time`): Time object of skyfield.timelib module
        satellite (:obj:`EarthSatellite`): Skyview EarthSatellite object from skyfield.sgp4lib module
        grounds (:obj:`DataFrame`): Dataframe of ground station locations, minimum elevation angles for communication, and operational status (T/F)

    Returns:
        bool, int :
            isInRange
                True/False indicating visibility of satellite to any operational ground station
            groundId
                groundId of the ground station currently in comm range (NOTE: If in range of two ground stations simultaneously, will return first groundId)
    """
    isInRange = False
    groundId = None
    for k, ground in grounds.iterrows():
        if ground.operational:
            groundLatLon = wgs84.latlon(ground.latitude, ground.longitude)
            satelliteElevation = get_elevation_angle(t, satellite, groundLatLon)
            if satelliteElevation >= ground.elevAngle:
                isInRange = True
                groundId = k
                break
    return isInRange


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

# name guard used to ensure script only executes if it is run as the __main__
if __name__ == "__main__":
    # Note that these are loaded from a .env file in current working directory
    credentials = dotenv_values(".env")
    SMCE_HOST, SMCE_PORT = credentials["SMCE_HOST"], int(credentials["SMCE_PORT"])
    SMCE_USERNAME, SMCE_PASSWORD = credentials["SMCE_USERNAME"], credentials["SMCE_PASSWORD"]

    CLIENT = mqtt.Client()
    CLIENT.username_pw_set(username=SMCE_USERNAME, password=SMCE_PASSWORD)
    CLIENT.tls_set()
    CLIENT.connect(SMCE_HOST, SMCE_PORT)
    CLIENT.loop_start

    while True:
        eph = load('de421.bsp')
        earth = eph['earth']
        ts = load.timescale()
        now = datetime.utcnow()
        current_time = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)

        sat_url = "https://celestrak.com/NORAD/elements/active.txt"
        satellites = load.tle_file(sat_url)
        by_name = {sat.name: sat for sat in satellites}
        satellite_list = ['ISS (ZARYA)', 'AQUA', 'TERRA', 'SUOMI NPP']
        #ISS = red, AQUA = blue, TERRA = green, SUOMI = yellow

        for name in satellite_list:
            satellite = by_name[name]
            satellite_LAT, satellite_LNG = wgs84.latlon_of(satellite.at(current_time))
            
            satellite_LATdeg = satellite_LAT.degrees
            satellite_LNGdeg = satellite_LNG.degrees

            alt = wgs84.subpoint(satellite.at(satellite.epoch)).elevation.m
            min_elev = compute_min_elevation(alt, FIELD_OF_REGARD)
            sens_radius = compute_sensor_radius(alt, min_elev)
            

            for i, row in GROUND.iterrows():
                groundID = row['groundId']
                lat = row['latitude']
                lng = row['longitude']
                ang = row['elevAngle']
                groundPOS = wgs84.latlon(lat, lng)
                inView = check_in_view(current_time, satellite, groundPOS, min_elev)
                range = check_in_range(current_time, satellite, GROUND)
                min_elev = compute_min_elevation(alt, FIELD_OF_REGARD)
                distance_to_grnd = haversine(lng, lat, satellite_LNGdeg, satellite_LATdeg)
                
                fspl_non = fspl_nondb(distance_to_grnd, uplink)
                fspl_dec = fspl_db(distance_to_grnd, uplink)
                signal_loss_dBW = signal_loss(power, fspl_dec)
                
                satellite_info = (f"DESIGNATOR: {satellite}, "
                                 f"GROUND STN #: {groundID}, "
                                 f"Latitude/Longitude: {satellite_LATdeg}, {satellite_LNGdeg}, "
                                 f"Minimum Viewing Angle: {min_elev}, " 
                                 f"Distance to ground station: {distance_to_grnd}, "
                                 f"Satellite in view & in range? {inView},{range}"
                                  )
                if name == 'ISS (ZARYA)':
                    CLIENT.publish(SAT_TPC1, satellite_info)
                    if inView and range:
                        signal_info = (f"FSPL (dB): {fspl_dec}, ")
                        CLIENT.publish(SAT_TPC1, signal_info)
                    time.sleep(0.5)
                elif name == 'AQUA':
                    CLIENT.publish(SAT_TPC2, satellite_info)
                    if inView and range:
                        signal_info = (f"FSPL (dB): {fspl_dec}, ")
                        CLIENT.publish(SAT_TPC2, signal_info)
                    time.sleep(0.5)
                elif name == 'TERRA':
                    CLIENT.publish(SAT_TPC3, satellite_info)
                    if inView and range:
                        signal_info = (f"FSPL (dB): {fspl_dec}, ")
                        CLIENT.publish(SAT_TPC3, signal_info)
                    time.sleep(0.5)
                else:
                    CLIENT.publish(SAT_TPC4, satellite_info)
                    if inView and range:
                        signal_info = (f"FSPL (dB): {fspl_dec}, ")
                        CLIENT.publish(SAT_TPC4, signal_info)
                    time.sleep(0.5)
                
          
           
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
    CLIENT.disconnect()
    CLIENT.loop_stop()
