import requests
import json
import logging

# NOTE - the IP address will be different based on the internet connection you are on.
# localhost been hardcoded only for development purposes for this prototype. 
post_zone_info_url = "http://pdq-api:5000/pdq/trucks"
post_van_coords_url = "http://pdq-api:5000/pdq/truckstartingcoordinates"


def POSTTruckLoc(url, truck_loc_json):
    res = requests.post(url=url, json=truck_loc_json)
    return res.text

def REQTruckLoc(url):
    res = requests.get(url=url)
    return res.text

def POSTTruckInfo(url, truck_info_json):
    res = requests.post(url=url, json=truck_info_json)
    return res.text

def REQTruckInfo(url):
    res = requests.get(url=url)
    return res.text

#format coordinate to fit the database schema.
def formatCoords(data):
    van_coord_arr = []
    coord_arr = data.split("|")

    for entry in coord_arr:
        coord_string = entry.replace("'", "\"")
        coord_dict = json.loads(coord_string)

        truckid_string = int(coord_dict["TruckId"])
        coord_point_arr = coord_dict["coordinates"].split(",")
        latitude = float(coord_point_arr[0])
        longitude = float(coord_point_arr[1])
        format_string = {"TruckId": truckid_string, "Latitude": latitude, "Longitude": longitude}

        van_coord_arr.append(format_string)
       
    return van_coord_arr




def main():
    print("API module started.")
    logging.info("API connection module started.")
    with open('data/truck_coords.txt', 'r') as f:
        data = f.read()

    json_data_arr = formatCoords(data)

    print("\nPosting to cloud database...")
    for json in json_data_arr:
        print("POSTING: " + str(json))
        res = POSTTruckLoc(post_van_coords_url, json)
        logging.info("SERVER RESPONSE: " + res)
    print("Success!\nKeep the API running to connect with android app, or ctrl+c to exit.")
  
main()

if __name__ == "__main__":
  main()
