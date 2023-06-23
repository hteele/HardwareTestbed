import os
import pandas as pd

PREFIX = os.getenv("PREFIX", "hawthorne")
NAME = os.getenv("NAME", "Grounds")
LOG = f"\x1b[1m[\x1b[32m{NAME}\x1b[37m]\x1b[0m"
HEADER = {
    "name": NAME,
    "description": f'Broadcasts it\'s location to the testbed on the "{PREFIX}/ground/location" topic.',
}

TPC1 = f"{PREFIX}/signals/strength"
TPC2 = f"{PREFIX}/signals/satellite_info"

SAT_TPC1 = f"{PREFIX}/signals/ISS"
SAT_TPC2 = f"{PREFIX}/signals/AQUA"
SAT_TPC3 = f"{PREFIX}/signals/TERRA"
SAT_TPC4 = f"{PREFIX}/signals/SUOMI"

power = 25 # Watts
uplink = 145.2 #MHz

LAT = 78.229772
LNG = 15.407786
MIN_ELEVATION = 5.0  # minimum view angle (degrees) for ground-satellite communications
FIELD_OF_REGARD = 112.56

"""

0 = Svalbard Station, Norway
1 = Madley Comms, England
2 = Goldstone DSCC, California
3 = Canberra DSCC, Australia

"""

GROUND = pd.DataFrame(
    data={
        "groundId": [0, 1, 2, 3, 4, 5, 6, 7],
         "latitude": [35.0, 30.0, -5.0, -30.0, 52.0, -20.0, 75.0, 40.74],
        "longitude": [-102.0, -9.0, -60.0, 25.0, 65.0, 140.0, -40.0, -74.03],
        "elevAngle": [5.0, 15.0, 5.0, 10.0, 5.0, 25.0, 15.0, 5.0],
        "operational": [True, True, True, True, True, True, True, True],
    }
)