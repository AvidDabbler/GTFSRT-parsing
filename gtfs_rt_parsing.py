from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import os
import zipfile
from urllib.request import urlopen
import pandas as pd
import json
import time
import csv
from collections import OrderedDict

####################################################################################
################################### OBJECTIVES ####################################
# FIND RUNNING TIMES FOR TRANSIT SYSTEM (FIRST RUN & LAST RUN)
# GET DATA TO RUN IN AN INTERVAL
# ENRICH REALTIME DATA WITH GTFS (USING PANDAS???)
# CHECK FOR UP TO DATE DATA AND UPDATE DATASET
# SAVE
####################################################################################

dir = os.getcwd()

def getGTFS():
    gtfs = [
        os.path.join(dir, 'agency.txt'),
        os.path.join(dir, 'calendar.txt'),
        os.path.join(dir, 'calendar_dates.txt'),
        os.path.join(dir, 'routes.txt'),
        os.path.join(dir, 'shapes.txt'),
        os.path.join(dir, 'stop_times.txt'),
        os.path.join(dir, 'stops.txt'),
        os.path.join(dir, 'transfers.txt'),
        os.path.join(dir, 'trips.txt'),
    ]
    for file in gtfs:
        if os.path.exists(file):
            os.remove(file)
    print("**********************************************")
    print("STARTING GTFS FETCH...")
    print("**********************************************")
    url = 'https://metrostlouis.org/Transit/google_transit.zip'

    print('FETCHING GTFS...')

    zipresp = urlopen(url) # Create a new file on the hard drive
    tempzip = open("google_transit.zip", "wb") # Write the contents of the downloaded file into the new file
    tempzip.write(zipresp.read()) # Close the newly-created file
    tempzip.close() # Re-open the newly-created file with ZipFile()

    zf = zipfile.ZipFile("google_transit.zip") # Extract its contents into <extraction_path> *note that extractall will automatically create the path
    zf.extractall(dir) # close the ZipFile instance
    zf.close()
    os.remove(fr"{dir}\\google_transit.zip")

    print(f'FETCHED GTFS => {dir}')
    print("**********************************************")
    print("ENDING GTFS FETCH...")
    print("**********************************************")
    print(' ')


def getRealTime():
    def saveTempData(d, filename):
        with open(filename, "w") as f:
            f.write(f'{d}')
            f.close()

        print(' ')
        print("************************************")
        print(f'{filename} created!')
        print("************************************")
        print(' ')

    def parseDict(u):
        # TAKES THE DATA FROM U (THE PB URL) AND TURNS IT INTO A DICTIONARY
        feed = gtfs_realtime_pb2.FeedMessage()
        url = u
        response = requests.get(url)
        feed.ParseFromString(response.content)
        feed2 = MessageToDict(feed)
        return feed2

    def loadRoutes(routesFile):
        routesJson = {}
        id = 0
        with open(routesFile, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                routesJson[id] = {}
                for key in line:
                    routesJson[id][key] = line[key]
                id += 1
        return routesJson

    routesJson = loadRoutes(r'routes.txt')

    def getVehicles(pburl):
        def addVehicleInfo(routes, vehicles):
            for vehicle in vehicles['features']:
                routei = 0
                while vehicle['data']['routeId'] != routesJson[routei]['ï»¿route_id']: # 'ï»¿route_id' is the default name for whatever reason for 'route_id'
                    routei += 1
                if vehicle['data']['routeId'] != routesJson[routei]['ï»¿route_id']:
                    routei = 0

                vehicle['data']['route_short_name'] = routesJson[routei]['route_short_name']
                vehicle['data']['route_long_name'] = routesJson[routei]['route_long_name']
            return vehicles

        def addVehiclePopups(vehicles):
            for vehicle in vehicles['features']:
                vehicle["properties"]["popupContent"] = f"Route: {vehicle['data']['route_short_name']} <br>Route Name: {vehicle['data']['route_long_name']} <br>TripID: {vehicle['data']['tripId']} <br>VehicleID: {vehicle['data']['vehicleId']}"
            return vehicles

        allVehicles = {}
        allVehicles['type'] = {}
        allVehicles['type'] = 'Feature Collection'
        allVehicles['features'] = []

        feed = parseDict(pburl)
        id = 0
        for value in feed['entity']:
            obj = {}

            # LIST OF SECTIONS
            list = ["type", "properties", "geometry", "data"]
            for i in list: # CREATE SECTIONS
                obj[i] = {}
            obj["type"] = "Feature"

            # START OF DATA SECTION
            tripId = value["vehicle"]["trip"]["tripId"]
            uni = obj["data"]
            uni["vehicleId"] = value["vehicle"]["vehicle"]["id"]
            uni["tripId"] = tripId
            uni["routeId"] = value["vehicle"]["trip"]["routeId"]
            uni["coordinates"] = [value["vehicle"]["position"]["longitude"], value["vehicle"]["position"]["latitude"]]

            # START OF GEOMETRY SECTION
            obj["geometry"]["type"] = "Point"
            obj["geometry"]["coordinates"] = uni["coordinates"]


            # START OF PROPERTIES SECTION
            obj["properties"] = {}
            obj["properties"]['id'] = id

            # ADD INDIVIDUAL VEHICLES TO LIST
            id += 1
            allVehicles['features'].append(obj)
        allVehicles = addVehicleInfo(routesJson, allVehicles)
        allVehicles = addVehiclePopups(allVehicles)
        return json.dumps(allVehicles)

    def getTrips(pburl):
        allTrips = {}
        feed = parseDict(pburl)
        for value in feed['entity']:
            tripId = value['tripUpdate']['trip']['tripId']
            allTrips[tripId] = {}
            allTrips[tripId]['tripId'] = tripId
            allTrips[tripId]['routeId'] = value['tripUpdate']['trip']['routeId']
            if 'delay' in value['tripUpdate']['stopTimeUpdate'][0]['departure']:
                allTrips[tripId]['delay'] = value['tripUpdate']['stopTimeUpdate'][0]['departure']['delay']

        return allTrips


    realtime_list = [
        'https://www.metrostlouis.org/RealTimeData/StlRealTimeVehicles.pb',
        'https://www.metrostlouis.org/RealTimeData/StlRealTimeTrips.pb'
    ]

    for item in realtime_list:

        # if looking at vehicles
        if item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeVehicles.pb':
            print('writing vehicles...')
            vehicles = getVehicles(item)
            saveTempData(vehicles, r'leaflet\vehicles.json')
            pass
        # if looking at the trips file
        elif item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeTrips.pb':
            print('writing trips...')
            print(item)
            trips = getTrips(item)
            saveTempData(trips, r'leaflet\trips.json')
            pass
        else:
            print(item)
            print('error')
            return



# getGTFS()
getRealTime()


# while 1==1:
#   getRealTime()
#   time.sleep(30)
