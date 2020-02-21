import os
import zipfile
from urllib.request import urlopen
import shutil

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


# getGTFS()
