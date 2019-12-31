import geopy
import string
from geopy.distance import VincentyDistance
from geopy.distance import distance
import logging 
import urllib.request
import urllib
import requests
import math
import json
import sys
import os

#Required to connect with Baidu map's API.
baidu_maps_key = 'guuGi0EAhhydtmT9FctncXgm4oZMSTGA'
baidu_base_request_url = 'http://api.map.baidu.com/direction/v2/driving?origin='

from collections import defaultdict

zone_info_dict = defaultdict(int)


def read_files():
    with open('data/service_area.txt', 'r') as area_f, open('data/zone_info.txt', 'r') as zone_f:
        service_area = str(area_f.read()).strip()

        zone_param_arr = []
        for line in zone_f:
            zone_param_arr.append(str(line).strip())
    
    for param in zone_param_arr:
        single_param = param.split('=')
        key = single_param[0]
        val = int(single_param[1])
        zone_info_dict[key] = val
        
    return service_area

service_area = read_files()   

num_of_vans = zone_info_dict['num_of_vans']
vans_per_zone = zone_info_dict['vans_per_zone']
num_of_zones = zone_info_dict['num_of_zones']

license_arr = []
for zone_cnt in range(num_of_vans):
    license_arr.append(zone_cnt)

supported_areas = defaultdict(str)
zone_dict = defaultdict(int)

for zone_cnt in range(num_of_zones):
    zone_dict[zone_cnt] = {}

van_dict = defaultdict(str)

for zone_cnt in range(num_of_vans):
    van_dict[license_arr[zone_cnt]] = {}

quadrant_bearing_dict = defaultdict(int)

quadrant_bearing_dict[0] = 45
quadrant_bearing_dict[1] = 135
quadrant_bearing_dict[2] = 225
quadrant_bearing_dict[3] = 315

# Reference point to create zone in an area. Suzhou, China is currently the only area supported. 
# Hardcoded for convenience in prototype.
supported_areas["suzhou"] = "31.322593,120.410113"


# Linear function to create delivery zones. Zones are created using circle geometry. 
# The center of the circle is the reference point used to create each zone, and this
# point represents the location of a pizza factory. The radius of the circle represents
# the distance from the pizza factory to any point on the edge of the delivery zone. 
# The function attempts to find a radius that will allow a maximum drive time of 45 minutes 
# to anywhere inside the zone from the factory, as per PDQ's requirement. The default area is Suzhou.
def create_zones(service_area="suzhou", num_of_zones=0, vans_per_zone=0, num_of_vans=0):
    print("Creating zones. This may take a few minutes...")
    
    zone_center_coords = supported_areas[str(service_area)]
    
    zone_cnt = 0
  

   
    while zone_cnt < num_of_zones:
        d = 1
        quadrant_cnt = zone_cnt % 4
        b = quadrant_bearing_dict[quadrant_cnt]
        map_travel_time = 0
  
    
        while map_travel_time < 60:
            map_travel_time = getTravelTime(d,zone_center_coords, b)
            low_bound = d
            d*=2
        
        high_bound = d

        # determine the best distance. The best distance is defined as the closest distance that has a travel time no less than
        # a specified target(in minutes) by driving. 
        best_d = binary_search(target=60,low=low_bound,high=high_bound, ref_point=zone_center_coords, degrees=b)
        dest_string = getDestination(best_d, zone_center_coords, b)
        
        zone_dict[zone_cnt]["ref_point"] = zone_center_coords
        zone_dict[zone_cnt]["radius"] = best_d
        zone_dict[zone_cnt]["direction_degrees"] = b
     
        zone_cnt += 1
        zone_center_coords = dest_string
        
        print("Ref. point: " ,dest_string)
        print("Created ", zone_cnt, " zones.")
        print("-----------------------")

        
        
    
def getDestination(dist, ref_point, degrees):
    
    destination = distance(kilometers=dist).destination(ref_point, degrees)
    lat2, lon2 = str(destination.latitude), str(destination.longitude)

    dest_string = ",".join(list([lat2,lon2]))
    return dest_string

def getTravelTime(distance, ref_point, degrees):

    dest_string = getDestination(distance,ref_point, degrees)

    status_code = -1
    logging.debug("Started connecting to Baidu Map API")
    while status_code != 0:

        logging.debug("Network error while connecting to Baidu Maps API. Retrying...")
        
        response_json = sendRequest(ref_point, dest_string)
        status_code = response_json["status"]

    baidu_travel_duration_mins = int(response_json["result"]["routes"][0]["duration"])/60

    return baidu_travel_duration_mins

def sendRequest(zone_center_coords,dest_string, attempts=3):
    if(attempts == 0):
        print("No network connection. Application terminating.")
        sys.exit(1)

    requestURL = baidu_base_request_url + zone_center_coords + '&destination=' + dest_string + '&ak=' + baidu_maps_key
    r = None
    try:
        request = urllib.request.Request(requestURL)
        response = urllib.request.urlopen(request)
        r = response.read().decode(encoding="utf-8")

    except Exception as e:
        logging.error("Error connecting to baidu maps. " + str(attempts) + " tries remaining...")
        sendRequest(zone_center_coords,dest_string, attempts -1)

    
    result = json.loads(r)
    return result

#Linear function to place coordinates representing the starting locations of each van inside each zone.
def placeVans():
    van_cnt = 0 
    zone_cnt = 0
    while zone_cnt < len(zone_dict) and van_cnt < num_of_vans:

        vans_in_zone = 0
        while vans_in_zone < vans_per_zone:

            license_num = license_arr[van_cnt]
            van_dict[license_num]["TruckId"] = van_cnt
            van_dict[license_num]["ref_point"] = str(zone_dict[zone_cnt]["ref_point"])
            km_distance = int((zone_dict[zone_cnt]["radius"]) / 2)

            van_dict[license_num]["distance"] = km_distance         
            van_dict[license_num]["direction"] = int(quadrant_bearing_dict[vans_in_zone])
        
            km = int(van_dict[license_num]["distance"])
            ref = str(van_dict[license_num]["ref_point"])
            bearing = int(van_dict[license_num]["direction"])
           
            van_coords = distance(kilometers=km).destination(ref, bearing)
            lat1, lon1 = str(van_coords.latitude), str(van_coords.longitude)
            van_coords = ",".join(list([lat1, lon1]))

            
            van_dict[license_num]["coordinates"] = van_coords
            van_dict[license_num]["zone"] = zone_cnt 
            vans_in_zone += 1
            van_cnt += 1
        zone_cnt += 1
    return

#Uses a binary search to determine the closest coordinate that is a specified travel time away from a specified reference point
# The target distance is set to 60 minutes by default, which allows the delivery truck driver a 15 minute buffer to deliver within 45 minutes.
# A linear search may be faster in cases where the target is less than 60. 
def binary_search(target=60, low=0, high=None, ref_point=None, degrees=None):
    diff = high - low
    mid = math.floor((high+low) / 2)
    time = getTravelTime(mid,ref_point, degrees)
    if diff < 2:
        #time = getTravalTime(low,ref_point, degrees)
        if  time >= target:
            while time >= target:
                low -= 1
                time = getTravelTime(low,ref_point, degrees)
            return low + 1
        
        else:
            while time <= target:
                low += 1
                time = getTravelTime(low,ref_point, degrees)
            return low
    else:
        if time >= target:
            high = mid
        else:
            low = mid
    return binary_search(target, low, high, ref_point, degrees)
         
def writeToFiles():
    string_arr = []
    for key in van_dict:
        string_arr.append(str(van_dict[key]))
    info_string = "|".join(string_arr)

    with open('data/truck_coords.txt', 'w+') as f:       
            f.write(info_string)

create_zones(service_area,num_of_zones,vans_per_zone,num_of_vans)
placeVans()
writeToFiles()

from connection import API_connect
API_connect

