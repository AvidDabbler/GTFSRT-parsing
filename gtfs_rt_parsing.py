from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import os
import zipfile
from urllib.request import urlopen
import json
import time
import csv

####################################################################################
################################### OBJECTIVES ####################################
# FIND RUNNING TIMES FOR TRANSIT SYSTEM (FIRST RUN & LAST RUN)
# ADD IN ACTIVE TRIPS FOR STOPS
# ADD IN NEXT TRIP / ROUTE ARRIVAL TIME (IF ANY) FOR STOP
# IF NO TRIP IS ASSIGNED OR REALTIME DATA NOT AVAILABLE STATE THAT IT IS NOT A REAL TIME AND PRINT NEXT ARRIVAL TIME
# CHECK FOR UP TO DATE DATA AND UPDATE DATASET
# RERUN GETGTFS() MONDAY AT 4AM (OK TO BREAK LOOP)
# SHUTDOWN AND RESTART PROCESS WHEN SERVICE NOT / IS AVAILABLE
####################################################################################

dir = os.getcwd()


def saveTempData(data, filename):
    with open(filename, "w") as f:
        jsondata = json.dumps(data, indent=2)
        f.write(f'{jsondata}')
        f.close()

    print(' ')
    print("************************************")
    print(f'{filename} created!')
    print("************************************")
    print(' ')

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
    os.remove(fr"{dir}/google_transit.zip")

    print(f'FETCHED GTFS => {dir}')
    print("**********************************************")
    print("ENDING GTFS FETCH...")
    print("**********************************************")
    print(' ')

def loadGTFS(routesFile, stopsFile, stopTimesFile):
    def loadRoutes(routesFile):
        routesJson = []
        with open(routesFile, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                data = {}
                for key in line:
                    if 'route_id' in key:
                        data['route_id'] = line[key]
                    else:
                        data[key] = line[key]
                routesJson.append(data)
        saveTempData(routesJson, r'leaflet\routes.json')

    def loadStops(stopTimesFile, stopsFile):
        geojson= {}
        geojson['type'] = "Feature Collection"
        geojson['features'] = []

        # LOAD UP STOPS.TXT FROM GTFS
        # !!! REFACTOR AS GEOJSON,

        stopsJson = []
        with open(stopsFile, newline='') as stops_csv:
            stopsReader = csv.DictReader(stops_csv)
            id = 0
            for stps in stopsReader:
                # CREATE AN OBJECT FOR EVERY STOP_ID
                indivStop = {}

                indivStop['data'] = {}
                indivStop['type'] = "Feature"
                indivStop['properties'] = {}

                indivStop['properties']['id'] = id
                indivStop['properties']['popup'] = f"Stop Name: {stps['stop_name']}"
                id += 1

                # ADD COLUMNS AS KEYS TO STOP
                for key in stps:
                    # RENAME STOP_ID KEY
                    if key == 'ï»¿stop_id':
                        indivStop['data']['stop_id'] = stps[key]
                    else:
                        indivStop['data'][key] = stps[key]
                    indivStop['data']['trips'] = []

                    indivStop['geometry'] = {}
                    indivStop['geometry']['type'] = "Point"
                    indivStop['geometry']['coordinates'] = [float(stps['stop_lon']), float(stps['stop_lat'])]

                stopsJson.append(indivStop)


        # # LOAD UP STOP_TIMES.TXT FROM GTFS
        # with open(stopTimesFile, newline='') as stop_times_csv:
        #     stopTimesReader = csv.DictReader(stop_times_csv)
        #     for stp_times in stopTimesReader:
        #         if stp_times['trip_id'] not in stopsJson['features'][stp_times['stop_id']]['data']['trips']:
        #             stopsJson[stp_times['stop_id']]['data']['trips'].append(stp_times['trip_id'])

        # CREATION OF GEOJSON FORMATTING FOR STOP.JSON
        geojson['type'] = "Feature Collection"
        geojson['features'] = stopsJson

        saveTempData(geojson, r'leaflet\stops.json')

    loadRoutes(routesFile)
    loadStops(stopTimesFile, stopsFile)

def getRealTime():
    # !!! ADD STOP ARRIVAL INFORMATION (POPUPS AND DATA FROM TRIPS.JSON)
    # !!! WILL NEED TO FIND STOP_ID IN TRIPS.JSON AND STOP_TIMES.TXT
    # FIND MATCHING STOP_ID / TRIP_ID SEQUENCE ADD NEW ARRIVAL TIME FROM STOP_TIMES.TXT

    def parseDict(pbu):
        # TAKES THE DATA FROM U (THE PB URL) AND TURNS IT INTO A DICTIONARY
        feed = gtfs_realtime_pb2.FeedMessage()
        url = pbu
        response = requests.get(url)
        feed.ParseFromString(response.content)
        feed2 = MessageToDict(feed)
        return feed2

    def getVehicles(pburl):
        def addVehicleInfo(vehicles):
            with open(r'leaflet\routes.json') as data:
                routesJson = json.loads(data.read())
                for vehicle in vehicles['features']:
                    routei = 0

                    # FINDING A ROUTE_ID MATCH BETWEEN VEHICLES AND ROUTESJSON. CYCLES THROUGH ROUTES TO FIND A MATCH
                    # !!! ASSUMES THAT THERE WILL BE A MATCH. FACTOR IN A NO MATCH BY LOOKING FOR END OF ROUTES LIST.
                    while vehicle['data']['routeId'] != routesJson[routei]['route_id']:
                        routei += 1

                    # IF ROUTE_ID MATCH FOUND
                    if vehicle['data']['routeId'] != routesJson[routei]['route_id']:
                        routei = 0

                    # COPY OVER ROUTESJSON ROUTE_SHORT_NAME AND ROUTE_LONG_NAME TO VEHICLES
                    vehicle['data']['route_short_name'] = routesJson[routei]['route_short_name']
                    vehicle['data']['route_long_name'] = routesJson[routei]['route_long_name']
                    vehicle['data']['route_full_name'] = routesJson[routei]['route_short_name'] + " " + routesJson[routei]['route_long_name']

                return vehicles

        def addVehiclePopups(vehicles):
            for vehicle in vehicles['features']:
                vehicle["properties"]["popupContent"] = f"Route: {vehicle['data']['route_short_name']} " \
                                                        f"<br>Route Name: {vehicle['data']['route_long_name']} " \
                                                        f"<br>TripID: {vehicle['data']['tripId']} " \
                                                        f"<br>VehicleID: {vehicle['data']['vehicleId']}"
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
        allVehicles = addVehicleInfo(allVehicles)
        allVehicles = addVehiclePopups(allVehicles)
        return allVehicles

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
            if 'delay' in value['tripUpdate']['stopTimeUpdate'][0]['departure']:
                allTrips[tripId]['time'] = value['tripUpdate']['stopTimeUpdate'][0]['departure']['time']
            if 'delay' in value['tripUpdate']['stopTimeUpdate'][0]['departure']:
                allTrips[tripId]['nextStopId'] = value['tripUpdate']['stopTimeUpdate'][0]['stopId']

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



getGTFS()
loadGTFS(r'routes.txt', r'stops.txt', r'stop_times.txt')
getRealTime()


# while 1==1:
#   getRealTime()
#   time.sleep(15)
