'''Creation of a Location class, as well as all tools needed for location.

'''
import re
from time import time

import standardise
import googlemaps

from key import key

# Create a googlemaps API client
GM = googlemaps.Client(key=key)

# Using the googlemaps API client, get the current locaiton
current_location_data = GM.geolocate(consider_ip=True)["location"]
CURRENT_LOCATION = (
    str(current_location_data["lat"])
    +","
    +str(current_location_data["lng"])
    )

# The datum currently in use by the system
datum = "Airy 1830" # Default is the UK datum

########## Possibly move to class, but defo talk about it later


# Regex patterns used for detection of form
LAT_LON_D_RE = re.compile(
    "[\d]{3}(\.[\d]+)?['°][\s+,][\d]{3}(\.[\d]+)?['°]$"
    )
LAT_LON_M_RE = re.compile(
    "[\d]{3}°[\d]{2}'[\d]{2}''[\s+,][\d]{3}°[\d]{2}'[\d]{2}''$"
    )
GRID_REF_RE = re.compile(
    "[a-zA-Z]{2}\s*"\
    "([\d]{2}\s*[\d]{2}"\
    "|[\d]{3}\s*[\d]{3}"\
    "|[\d]{4}\s*[\d]{4}"\
    "|[\d]{5}\s*[\d]{5})$"
    )
EA_NO_RE = re.compile(
    "[\d]+[\s*,][\d]+$"
    )


class Location:
    '''Allows for abtraction of data about a given point to a single location

    By collecting all the needed data about a user's input and then
    standadising the input, the specifics of the location can be abstacted
    away. Every location will have the data in the same form that can be used
    by a system.

    Attributes:
    user_input         Initlization variable
    location           A standadised version of what the user has inputted
    ID                 Unquie ID for the object

    Methods:
    standardise    Calculates a standard form of the user's inputted value
    '''
    def __init__(self, user_input):
        self.user_input = user_input
        self.location = self.standardise(user_input)
        self.ID = time()

    def __repr__(self):
        return self.location

    def standardise(self, user_input):
        '''Take the user's input and return a standadised form

        Parameters:
        user_input         The input to be standadised
        '''

        # Perform comparisions with Regex until a match and then convert
        if re.match(LAT_LON_D_RE, user_input):
            return user_input
        elif re.match(LAT_LON_M_RE, user_input):
            return standadise.degrees_min_to_degrees_dec(user_input)
        elif re.match(GRID_REF_RE, user_input):
            return standadise.map_ref_convert(user_input, datum)
        elif re.match(EA_NO_RE, user_input):
            return standadise.northing_easting_to_degrees(user_input, datum)
        else:
            lat_lon_data = GM.geocode(user_input)[0]["geometry"]["location"]
            lat = str(lat_lon_data["lat"])
            lon = str(lat_lon_data["lng"])
            lat_lon = lat+","+lon
            return lat_lon

