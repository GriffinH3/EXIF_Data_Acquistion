'''
John Griffin Harrington 
September 18, 2020
EXIF Data Acquistion
'''

'''
1) The user enters a path to a directory containing jpeg files.
2) Using that path, process all the .jpg files contained in that folder  (use the testimages.zip set of images).
3) Extracts, EXIF data from each of the images and create a pretty table output.

'''

''' LIBRARY IMPORT SECTION '''

import os                       
import sys                      
from datetime import datetime   

# import the Python Image Library 
# along with TAGS and GPS related TAGS
# Note you must install the PILLOW Module
# pip install PILLOW

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# import the prettytable library
from prettytable import PrettyTable

def ExtractGPSDictionary(fileName):
    ''' Function to Extract GPS Dictionary '''
    try:
        pilImage = Image.open(fileName)
        exifData = pilImage._getexif()

    except Exception:
        # If exception occurs from PIL processing
        # Report the 
        return None, None

    # Interate through the exifData
    # Searching for GPS Tags

    imageTimeStamp = "NA"
    cameraModel = "NA"
    cameraMake = "NA"
    gpsData = False

    gpsDictionary = {}

    if exifData:

        for tag, theValue in exifData.items():

            # obtain the tag
            tagValue = TAGS.get(tag, tag)
            
            # Collect basic image data if available

            if tagValue == 'DateTimeOriginal':
                imageTimeStamp = exifData.get(tag).strip()

            if tagValue == "Make":
                cameraMake = exifData.get(tag).strip()

            if tagValue == 'Model':
                cameraModel = exifData.get(tag).strip()

            # check the tag for GPS
            if tagValue == "GPSInfo":

                gpsData = True;

                # Found it !
                # Now create a Dictionary to hold the GPS Data

                # Loop through the GPS Information
                for curTag in theValue:
                    gpsTag = GPSTAGS.get(curTag, curTag)
                    gpsDictionary[gpsTag] = theValue[curTag]

        basicExifData = [imageTimeStamp, cameraMake, cameraModel]    

        return gpsDictionary, basicExifData

    else:
        return None, None

# End ExtractGPSDictionary ============================


def ExtractLatLon(gps):
    ''' Function to Extract Lattitude and Longitude Values '''

    # to perform the calcuation we need at least
    # lat, lon, latRef and lonRef
    
    try:
        latitude     = gps["GPSLatitude"]
        latitudeRef  = gps["GPSLatitudeRef"]
        longitude    = gps["GPSLongitude"]
        longitudeRef = gps["GPSLongitudeRef"]

        lat, lon = ConvertToDegreesV1(latitude, latitudeRef, longitude, longitudeRef)

        gpsCoor = {"Lat": lat, "LatRef":latitudeRef, "Lon": lon, "LonRef": longitudeRef}

        return gpsCoor

    except Exception as err:
        return None

# End Extract Lat Lon ==============================================


def ConvertToDegreesV1(lat, latRef, lon, lonRef):
    
    degrees = lat[0]
    minutes = lat[1]
    seconds = lat[2]
    latDecimal = float ( (degrees +(minutes/60) + (seconds)/(60*60) ) )
    if latRef == 'S':
        latDecimal = latDecimal*-1.0
        
    degrees = lon[0]
    minutes = lon[1]
    seconds = lon[2]
    lonDecimal = float ( (degrees +(minutes/60) + (seconds)/(60*60) ) )
    
    if latRef == 'W':
        lonDecimal = lonDecimal*-1.0
    
    return(latDecimal, lonDecimal)


''' MAIN PROGRAM ENTRY SECTION '''

if __name__ == "__main__":
    '''
    pyExif Main Entry Point
    '''
    print("\nExtract EXIF Data from JPEG Files")

    print("Script Started", str(datetime.now()))
    print()

    ''' PROCESS EACH JPEG FILE SECTION '''

    latLonList = []
                    # file must be located in the same folder
    def processFile(targetFile):
        if os.path.isfile(targetFile):
            gpsDictionary, exifList = ExtractGPSDictionary(targetFile)
                
            if exifList:
                TS = exifList[0]
                MAKE = exifList[1]
                MODEL = exifList[2]
            else:
                TS = 'NA'
                MAKE = 'NA'
                MODEL = 'NA'
    
            
            if (gpsDictionary != None):
    
                # Obtain the Lat Lon values from the gpsDictionary
                # Converted to degrees
                # The return value is a dictionary key value pairs
    
                dCoor = ExtractLatLon(gpsDictionary)
    
    
                if dCoor:
                    lat = dCoor.get("Lat")
                    latRef = dCoor.get("LatRef")
                    lon = dCoor.get("Lon")
                    lonRef = dCoor.get("LonRef")
                    
                   
                resultTable.add_row([targetFile, lat, lon, TS, MAKE, MODEL])
            else:
                print("WARNING No GPS EXIF Data")
                
        else:
            print("WARNING", " not a valid file", targetFile)

    # Create Result Table Display using PrettyTable
    ''' GENERATE RESULTS TABLE SECTION'''

    ''' Result Table Heading'''
    resultTable = PrettyTable(['File-Name', 'Lat','Lon', 'TimeStamp', 'Make', 'Model'])
    ''' Your work starts here '''
    
    directory = input("Enter directory to process: ")
    while (not (os.path.isdir(directory))):
        directory = input("Enter directory to process: ")
    
    fileList = os.path.abspath(directory)
    with os.scandir(fileList) as dirs:
        for eachFile in dirs:
            try: 
                relPath = os.path.join(directory, eachFile)
                absPath = os.path.abspath(relPath)                
            except:
                continue
            print("\nProcessing File.... ", absPath)
            processFile(absPath)
            
    resultTable.align = 'l'       
    print(resultTable.get_string())
        
