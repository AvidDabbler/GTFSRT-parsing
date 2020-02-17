from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import os
import zipfile
from urllib.request import urlopen
import shutil
import pandas as pd
import time


####################################################################################
################################### OBJECTIVES ####################################
# FIND RUNNING TIMES FOR TRANSIT SYSTEM (FIRST RUN & LAST RUN)
# GET DATA TO RUN IN AN INTERVAL
# ENRICH REALTIME DATA WITH GTFS (USING PANDAS???)
# CHECK FOR UP TO DATE DATA AND UPDATE DATASET
# SAVE
####################################################################################


def getGTFS():
    print("**********************************************")
    print("STARTING GTFS FETCH...")
    print("**********************************************")
    url = 'https://metrostlouis.org/Transit/google_transit.zip'

    dir = os.getcwd()
    gtfs = os.path.join(dir, "files")

    if os.path.exists(gtfs):
        shutil.rmtree(gtfs)
    else:
        print('File does not exists')

    print('FETCHING GTFS...')

    zipresp = urlopen(url)
    # Create a new file on the hard drive
    tempzip = open("google_transit.zip", "wb")
    # Write the contents of the downloaded file into the new file
    tempzip.write(zipresp.read())
    # Close the newly-created file
    tempzip.close()
    # Re-open the newly-created file with ZipFile()
    zf = zipfile.ZipFile("google_transit.zip")
    # Extract its contents into <extraction_path>
    # note that extractall will automatically create the path
    zf.extractall(gtfs)
    # close the ZipFile instance
    zf.close()
    os.remove(fr"{dir}\\google_transit.zip")

    print(f'FETCHED GTFS => {gtfs}')
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
        feed = gtfs_realtime_pb2.FeedMessage()
        url = u
        response = requests.get(url)
        feed.ParseFromString(response.content)
        feed2 = MessageToDict(feed)
        return feed2

    def vehicle(pburl):
        allVehicles = {}
        allVehicles['Features'] = []

        feed = parseDict(pburl)
        for value in feed['entity']:
            obj = {}

            # LIST OF SECTIONS
            list = ['type', 'properties', 'geometry', 'data']
            for i in list:  # CREATE SECTIONS
                obj[i] = {}
            obj['type'] = 'Feature'

            # START OF DATA SECTION
            tripId = value['vehicle']['trip']['tripId']
            uni = obj['data']
            uni['vehicleId'] = value['vehicle']['vehicle']['id']
            uni['tripId'] = tripId
            uni['routeId'] = value['vehicle']['trip']['routeId']
            uni['coordinates'] = [value['vehicle']['position']['latitude'], value['vehicle']['position']['longitude']]

            # START OF GEOMETRY SECTION
            obj['geometry']['type'] = 'Point'
            obj['geometry']['coordinates'] = uni['coordinates']

            # START OF PROPERTIES SECTION
            obj['properties'] = {}
            obj['properties'][
                'popupContent'] = f"RouteID: {uni['routeId']} <br>TripID: {uni['tripId']} <br>VehicleID: {uni['vehicleId']}"

            # ADD INDIVIDUAL VEHICLES TO LIST
            allVehicles['Features'].append(obj)
        return allVehicles

    def trip(pburl):
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
        print(item)
        # if looking at vehicles
        if item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeVehicles.pb':
            print('writing vehicles...')
            vehicles = vehicle(item)
            saveTempData(vehicles, 'vehicles.json')
            pass
        # if looking at the trips file
        elif item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeTrips.pb':
            print('writing trips...')
            print(item)
            trips = trip(item)
            saveTempData(trips, 'trips.json')
            pass
        else:
            print(item)
            print('error')
            return


def addTripUpdate(gtfs_trips, trips):
    trps = trips['trips']['id']
    for t in trps:
        print(t[0])

    gtfs_trips['update'] = 999


getGTFS()
getRealTime()
