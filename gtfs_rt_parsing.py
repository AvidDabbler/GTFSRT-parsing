from google.transit import gtfs_realtime_pb2
import requests
import os
import zipfile
from urllib.request import urlopen
import shutil
import pandas as pd

####################################################################################
################################### OBJECTIVES ####################################
# FIND RUNNING TIMES FOR TRANSIT SYSTEM (FIRST RUN & LAST RUN)
# GET DATA TO RUN IN AN INTERVAL
# ENRICH REALTIME DATA WITH GTFS (USING PANDAS???)
# CHECK FOR UP TO DATE DATA AND UPDATE DATASET
# SAVE
####################################################################################

data = {}


def getGTFS():
  print("**********************************************")
  print("STARTING GTFS FETCH...")
  print("**********************************************")
  url = 'https://url-to-transit-agencies-gtfs.com/gtfs/'

  dir = os.getcwd()
  gtfs = os.path.join(dir, "files")

  if os.path.exists(gtfs):
    shutil.rmtree(gtfs)
  else:
    print('File does not exists')

  print('FETCHING GTFS...')

  zipresp = urlopen(url)
  tempzip = open("google_transit.zip", "wb")
  tempzip.write(zipresp.read())
  tempzip.close()
  zf = zipfile.ZipFile("google_transit.zip")
  zf.extractall(gtfs)
  zf.close()
  os.remove(fr"{dir}\\google_transit.zip")

  print(f'FETCHED GTFS => {gtfs}')
  print("**********************************************")
  print("ENDING GTFS FETCH...")
  print("**********************************************")
  print(' ')


def getRealTime(obj):


  def vehicle(pburl):
    o = {}

    feed = gtfs_realtime_pb2.FeedMessage()
    url = pburl
    response = requests.get(url)
    feed.ParseFromString(response.content)

    for entity in feed.entity:
      if entity.HasField('vehicle'):
        o[entity.id] = entity
    return o

  def trips(pburl):
    o ={}
    feed = gtfs_realtime_pb2.FeedMessage()
    url = pburl
    response = requests.get(url)
    feed.ParseFromString(response.content)

    for entity in feed.entity:
      if entity.HasField('trip_update'):
        o[entity.id] = entity
    return o

  realtime_list = [
    'https://www.url-to-gtfs-rt.com/vehicles',
    'https://www.url-to-gtfs-rt.com/trips'
  ]

  for item in realtime_list:
    print(item)
    # if looking at vehicles
    if item == 'https://www.url-to-gtfs-rt.com/vehicles':
      print('writing vehicles...')
      data['vehicles'] = vehicle(item)
    # if looking at the trips file
    elif item == 'https://www.url-to-gtfs-rt.com/trips':
      print('writing trips...')
      print(item)
      data['trips'] = trips(item)
    else:
      print(item)
      print('error')


def saveTempData(d, filename):
  with open(filename, "w") as f:
    f.write(f'{d}')
    f.close()
  print(' ')
  print("************************************")
  print(f'{filename} created!')
  print("************************************")
  print(' ')



getGTFS()
getRealTime(data)
saveTempData(data,'data.json')
