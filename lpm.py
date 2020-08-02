
from selenium_module import *
from px_utils import *

import googlemaps


# get latitude and longitude of place
def loc_lat_lng(city):
    location = _GMAPS.geocode(city)
    lat = location[0]["geometry"]["location"]["lat"]
    lng = location[0]["geometry"]["location"]["lng"]
    location = (lat, lng)
    return location

def lpm(city):
    global _GMAPS
    
    from key import API_KEY
    _GMAPS = googlemaps.Client(key = API_KEY)
    
    zoom = 10
    resolution = "1080,1080"
    
    return sel_lpm(zoom, resolution)

def sel_lpm(zoom, resolution):
    for i in range(10):
        try:
            dv = boot(resolution)
            lp_map(dv, city, zoom)
            killd(dv)

            # closest spots for each radiance index
            spots = find_spot_edge()
            # location json
            location = loc_lat_lng(city)
            # location elevation json
            elev = _GMAPS.elevation(location)
            # closest unpolluted spot
            sp_coords = spot_coords(location, spots[1], zoom, resolution)
            # distance to the spot
            final_dist = _GMAPS.distance_matrix(location, sp_coords)['rows'][0]['elements'][0]['distance']['text']
            return(sp_coords)
        except Exception as e:
            print(e)
            zoom -= 1
            print("zooming out -", zoom)

if __name__ == '__main__':
    try:
        city = input("City: ")
        coords = lpm(city)
    except KeyboardInterrupt:
            exit(0)

'''
i = 0
max_h = 0
while i < len(elev2):
    temp = elev2[i]["elevation"]
    if temp > max_h:
        max_h = elev2[i]["elevation"]
        max_lat = elev2[i]["location"]["lat"]
        max_lng = elev2[i]["location"]["lng"]
        max_coords = (max_lat, max_lng)
    i += 1
print("max is: ", max_h)
print("max coordinates are: ", max_coords)
'''