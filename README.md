# GTFSRT-parsing
## Description
This script is meant to be used to work with [GTFS-RT](https://developers.google.com/transit/gtfs-realtime) and [GTFS](https://developers.google.com/transit/gtfs) data. The data displayed here is configured to the [Saint Louis Metro](https://www.metrostlouis.org/developer-resources/) GTFS and GTFS-RT feeds. Currently it is setup to only work with the Trip Updates and Vehicle Locations. GTFS and GTFS-RT feeds can vary by agency and should be looked into to make sure that the data schema lines up if you are attempting to use this for another agency. 
 
 To run execute the `gtfs_rt_parsing.py` file and the GTFS static feed will be downloaded and stored in .files and a vehicles.json and trips.json file will be created. 


## Files
The files in this repo that need to be executed are just the `gtfs_rt_parsing.py` file. This repo will run and other files will be populated in both the root folder and the leaflet folder so make sure that you have write access before executing this script. 

## gtfs_rt_parsing.py
This section will cover the breakdown of each function and its purposes. For documentation sake and deployability sake functions were created to break down sub processes.

### saveTempData()
Helper function that save data locally as a json file. 

### getGTFS()
This function does exactly what it says. It repopulates the GTFS fetch. It checks the root folder for the GTFS files, deletes them and then follows the `url` parameter to get the new GTFS.

### loadGTFS()
This function loads the gtfs into the `routes.json` == routesFile, `stops.json` == stopsFile, and `stopTimesFile.json` == stopTimesFile. These files are run at the bottom of the `def` with the corresponding subfunction. This script is only run at the begining because the data that is appended only needs to be applied when the GTFS file are changes upon fetch due to schedule changes. 
#### loadRoutes()
The `loadRoutes()` function loads the routesFile from the GTFS as a csv and turns it into a list of json objects and then stores that data locally in the leaflet folder. 
#### loadStops()
The `loadStops()` function loads the stopsFile from the GTFS as a csv and turns it into a list of json objects and then stores that data locally in the leaflet folder. After it is loaded it assigns all of the `trip_id`'s associated with it from the stopTimesFile.


### getRealTime()
This is where the realtime data or GTFS-RT is parsed through as json data in order for it to be displayed through the web. 

At the bottom of `getRealTime()` function the vehicles and trips protocol buffers will be fetched and saved in its proper location for leaflet to display.

#### parseDict()
This is a helper function used for the vehicle and trips Protocol Buffer information fetched from the GTFS-RT
#### getVehicles()
This overall function handles the formatting for the vehicles. helper functions are at the top and processing is done at the bottom.
##### addVehicleInfo()
This function uses the `routes.json` file to add in information to the realtime data from the static GTFS files via the routesJson (`routes.json`) file. Currently it looks at the route id's associated with the vehicles and adds the short name (public routed number) and route long name (public route name and number).
##### addVehiclePopups()
This function adds in the html formatting for the popups for the vehicles. It currently displays the route short name, route long name, trip id and vehicle id. 
#### getTrips()
This function handles the trip arrival information for all the trips and produces the `trips.json` file. This information will later be used to update the `stops.json` file with up to date information for route arrivals. 

All functions run at the end either as a loop or a single test. 