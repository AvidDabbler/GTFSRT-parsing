from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import os
import zipfile
from urllib.request import urlopen
import pandas as pd
import json
import time


dir = os.getcwd()
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


def getGTFS():
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

  def vehicle(pburl):
    allVehicles = {} # CREATE A NEW OBJECT FOR ALL OF THE VEHICLE INFORMATION
    allVehicles['type'] = {} # ADD TYPE
    allVehicles['type'] = 'Feature Collection' # SPECIFY TYPE = 'FEATURE COLLECTION' FOR GEOJSON FORMATTING
    allVehicles['features'] = [] # CREATE A LIST CALLED FEATURES TO HOLD ALL OF THE ATTRIBUTE AND LOCATIONAL DATA

    feed = parseDict(pburl) # PARSES PB VEHICLE DATA INTO A DICTIONARY
    id = 0 # VEHICLE ID STARTS AT 0
    for value in feed['entity']:
      obj = {} # CREATE A NEW OBJECT FOR EACH VEHICLE

      # LIST OF SECTIONS
      list = ["type", "properties", "geometry", "data"]
      for i in list: # CREATE SECTIONS
        obj[i] = {} # ADD A NEW OBJECT FOR EACH SECTION FOR GEOJSON, HTML FORMATTING AND DATA RETENTION
      obj["type"] = "Feature" # CLASSIFY "TYPE" AS A "FEATURE" FOR GEOJSON PURPOSES

      # START OF DATA SECTION
      tripId = value["vehicle"]["trip"]["tripId"]
      uni = obj["data"]

      # COPYING DATA OVER TO THE DATA SECTION OF THE GEOJSON OBJECT
      uni["vehicleId"] = value["vehicle"]["vehicle"]["id"]
      uni["tripId"] = tripId
      uni["routeId"] = value["vehicle"]["trip"]["routeId"]
      uni["coordinates"] = [value["vehicle"]["position"]["longitude"], value["vehicle"]["position"]["latitude"]]

      # START OF GEOMETRY SECTION
      obj["geometry"]["type"] = "Point"
      obj["geometry"]["coordinates"] = uni["coordinates"]


      # START OF PROPERTIES SECTION
      obj["properties"] = {}
      obj["properties"]["popupContent"] = f"RouteID: {uni['routeId']} <br>TripID: {uni['tripId']} <br>VehicleID: {uni['vehicleId']}"
      obj["properties"]['id'] = id

      # ADD INDIVIDUAL VEHICLES TO LIST
      id += 1
      allVehicles['features'].append(obj)
    return json.dumps(allVehicles)

  def trip(pburl):
    allTrips = {} # CREATES A NEW OBJECT FOR ALL OF THE TRIP DATA
    feed = parseDict(pburl) # PARSES THE TRIP PB DATA TO DICTIONARY
    for value in feed['entity']:
      tripId = value['tripUpdate']['trip']['tripId']
      allTrips[tripId] = {} # CREATES A NEW TRIP ID OBJECT FOR EACH TRIP IDENTIFIED
      allTrips[tripId]['tripId'] = tripId # COPY OVER TRIPID DATA FROM FEED
      allTrips[tripId]['routeId'] = value['tripUpdate']['trip']['routeId'] # COPY OVER ROUTEID
      if 'delay' in value['tripUpdate']['stopTimeUpdate'][0]['departure']:
        allTrips[tripId]['delay'] = value['tripUpdate']['stopTimeUpdate'][0]['departure']['delay']
    return allTrips


  realtime_list = [
    'https://www.metrostlouis.org/RealTimeData/StlRealTimeVehicles.pb',
    'https://www.metrostlouis.org/RealTimeData/StlRealTimeTrips.pb'
  ]

  # LOOPS THROUGH THE VEHICLES AND TRIPS PB DATA
  for item in realtime_list:
    print(item)

    # IF YOU ARE LOOKING AT THE VEHICLES PB FILE
    if item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeVehicles.pb':
      print('writing vehicles...')
      vehicles = vehicle(item)
      saveTempData(vehicles, r'leaflet/vehicles.json')
      pass

    # IF YOU ARE LOOKING AT THE TRIPS PB FILE
    elif item == 'https://www.metrostlouis.org/RealTimeData/StlRealTimeTrips.pb':
      print('writing trips...')
      print(item)
      trips = trip(item)
      saveTempData(trips, 'leaflet/trips.json')
      pass

    # ELSE THERE IS AN ERROR
    else:
      print(item)
      print('error')
      return




getGTFS()

while 1==1:
  getRealTime()
  time.sleep(30)