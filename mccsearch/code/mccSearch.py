#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from datetime import timedelta, datetime
import glob
import itertools
from netCDF4 import Dataset, date2num
import numpy as np
import numpy.ma as ma
import os
import pickle
import re
from scipy import ndimage
import string
import subprocess
import sys
import time

import networkx as nx
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, HourLocator
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import cm as cmbm
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter, FormatStrFormatter

import ocw.plotter as plotter

#----------------------- GLOBAL VARIABLES --------------------------
# --------------------- User defined variables ---------------------
# FYI the lat lon values are not necessarily inclusive of the points given. These are the limits
# the first point closest the the value (for the min) from the MERG data
# is used, etc.
LATMIN = '5.0'  # min latitude; -ve values in the SH e.g. 5S = -5
LATMAX = '19.0'  # max latitude; -ve values in the SH e.g. 5S = -5 20.0
LONMIN = '-5.0'  # min longitude; -ve values in the WH e.g. 59.8W = -59.8 -30
LONMAX = '5.0'  # min longitude; -ve values in the WH e.g. 59.8W = -59.8  30
XRES = 4.0  # x direction spatial resolution in km
YRES = 4.0  # y direction spatial resolution in km
TRES = 1  # temporal resolution in hrs
LAT_DISTANCE = 111.0  # the avg distance in km for 1deg lat for the region being considered
LON_DISTANCE = 111.0  # the avg distance in km for 1deg lon for the region being considered
# the matrix for determining the pattern for the contiguous boxes and must
STRUCTURING_ELEMENT = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
# have same rank of the matrix it is being compared against
# criteria for determining cloud elements and edges
# warmest temp to allow (-30C to -55C according to Morel and Sensi 2002)
T_BB_MAX = 243
T_BB_MIN = 218  # cooler temp for the center of the system
# the min temp/max temp that would be expected in a CE.. this is highly
# conservative (only a 10K difference)
CONVECTIVE_FRACTION = 0.90
MIN_MCS_DURATION = 3  # minimum time for a MCS to exist
# minimum area for CE criteria in km^2 according to Vila et al. (2008) is 2400
AREA_MIN = 2400.0
# km^2  from Williams and Houze 1987, indir ref in Arnaud et al 1992
MIN_OVERLAP = 10000.00

#---the MCC criteria
ECCENTRICITY_THRESHOLD_MAX = 1.0  # tending to 1 is a circle e.g. hurricane,
ECCENTRICITY_THRESHOLD_MIN = 0.50  # tending to 0 is a linear e.g. squall line
OUTER_CLOUD_SHIELD_AREA = 80000.0  # km^2
INNER_CLOUD_SHIELD_AREA = 30000.0  # km^2
OUTER_CLOUD_SHIELD_TEMPERATURE = 233  # in K
INNER_CLOUD_SHIELD_TEMPERATURE = 213  # in K
# min number of frames the MCC must exist for (assuming hrly frames, MCCs
# is 6hrs)
MINIMUM_DURATION = 6
MAXIMUM_DURATION = 24  # max number of framce the MCC can last for
#------------------- End user defined Variables -------------------
edgeWeight = [1, 2, 3]  # weights for the graph edges
# graph object fo the CEs meeting the criteria
CLOUD_ELEMENT_GRAPH = nx.DiGraph()
# graph meeting the CC criteria
PRUNED_GRAPH = nx.DiGraph()
#------------------------ End GLOBAL VARS -------------------------

#************************ Begin Functions *************************
#******************************************************************


def readMergData(dirname, filelist=None):
    '''
    Purpose::
            Read MERG data into RCMES format

    Input::
            dirname: a string representing the directory to the MERG files in NETCDF format
            filelist (optional): a list of strings representing the filenames betweent the start and end dates provided

    Output::
            A 3D masked array (t,lat,lon) with only the variables which meet the minimum temperature
            criteria for each frame

    Assumptions::
            The MERG data has been converted to NETCDF using LATS4D
            The data has the same lat/lon format

    TODO:: figure out how to use netCDF4 to do the clipping tmp = netCDF4.Dataset(filelist[0])

    '''

    global LAT
    global LON

    # these strings are specific to the MERG data
    mergVarName = 'ch4'
    mergTimeVarName = 'time'
    mergLatVarName = 'latitude'
    mergLonVarName = 'longitude'
    filelistInstructions = dirname + '/*'
    if filelist is None:
        filelist = glob.glob(filelistInstructions)

    # sat_img is the array that will contain all the masked frames
    mergImgs = []
    # timelist of python time strings
    timelist = []
    time2store = None
    tempMaskedValueNp = []

    filelist.sort()
    nfiles = len(filelist)

    # Crash nicely if there are no netcdf files
    if nfiles == 0:
        print("Error: no files in this directory! Exiting elegantly")
        sys.exit()
    else:
        # Open the first file in the list to read in lats, lons and generate
        # the  grid for comparison
        tmp = Dataset(filelist[0], 'r+', format='NETCDF4')

        alllatsraw = tmp.variables[mergLatVarName][:]
        alllonsraw = tmp.variables[mergLonVarName][:]
        alllonsraw[alllonsraw > 180] = alllonsraw[alllonsraw >
                                                  180] - 360.  # convert to -180,180 if necessary

        # get the lat/lon info data (different resolution)
        latminNETCDF = find_nearest(alllatsraw, float(LATMIN))
        latmaxNETCDF = find_nearest(alllatsraw, float(LATMAX))
        lonminNETCDF = find_nearest(alllonsraw, float(LONMIN))
        lonmaxNETCDF = find_nearest(alllonsraw, float(LONMAX))
        latminIndex = (np.where(alllatsraw == latminNETCDF))[0][0]
        latmaxIndex = (np.where(alllatsraw == latmaxNETCDF))[0][0]
        lonminIndex = (np.where(alllonsraw == lonminNETCDF))[0][0]
        lonmaxIndex = (np.where(alllonsraw == lonmaxNETCDF))[0][0]

        # subsetting the data
        latsraw = alllatsraw[latminIndex: latmaxIndex]
        lonsraw = alllonsraw[lonminIndex:lonmaxIndex]

        LON, LAT = np.meshgrid(lonsraw, latsraw)
        # clean up
        latsraw = []
        lonsraw = []
        nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])
        tmp.close

    for files in filelist:
        try:
            thisFile = Dataset(files, format='NETCDF4')
            # clip the dataset according to user lat,lon coordinates
            tempRaw = thisFile.variables[mergVarName][:,
                                                      latminIndex:latmaxIndex,
                                                      lonminIndex:lonmaxIndex].astype('int16')
            tempMask = ma.masked_array(
                tempRaw, mask=(
                    tempRaw > T_BB_MAX), fill_value=0)

            # get the actual values that the mask returned
            tempMaskedValue = ma.zeros((tempRaw.shape)).astype('int16')
            for index, value in maenumerate(tempMask):
                time_index, lat_index, lon_index = index
                tempMaskedValue[time_index, lat_index, lon_index] = value

            xtimes = thisFile.variables[mergTimeVarName]
            # convert this time to a python datastring
            time2store, _ = getModelTimes(xtimes, mergTimeVarName)
            # extend instead of append because getModelTimes returns a list already and we don't
            # want a list of list
            timelist.extend(time2store)
            mergImgs.extend(tempMaskedValue)
            thisFile.close
            thisFile = None

        except BaseException:
            print(("bad file! %s" % files))

    mergImgs = ma.array(mergImgs)

    return mergImgs, timelist
#******************************************************************


def findCloudElements(mergImgs, timelist, TRMMdirName=None):
    '''
    Purpose::
            Determines the contiguous boxes for a given time of the satellite images i.e. each frame
            using scipy ndimage package

    Input::
            mergImgs: masked numpy array in (time,lat,lon),T_bb representing the satellite data. This is masked based on the
            maximum acceptable temperature, T_BB_MAX
            timelist: a list of python datatimes
            TRMMdirName (optional): string representing the path where to find the TRMM datafiles

    Output::
            CLOUD_ELEMENT_GRAPH: a Networkx directed graph where each node contains the information in cloudElementDict
            The nodes are determined according to the area of contiguous squares. The nodes are linked through weighted edges.

            cloudElementDict = {'uniqueID': unique tag for this CE,
                                                    'cloudElementTime': time of the CE,
                                                    'cloudElementLatLon': (lat,lon,value) of MERG data of CE,
                                                    'cloudElementCenter':list of floating-point [lat,lon] representing the CE's center
                                                    'cloudElementArea':floating-point representing the area of the CE,
                                                    'cloudElementEccentricity': floating-point representing the shape of the CE,
                                                    'cloudElementTmax':integer representing the maximum Tb in CE,
                                                    'cloudElementTmin': integer representing the minimum Tb in CE,
                                                    'cloudElementPrecipTotal':floating-point representing the sum of all rainfall in CE if TRMMdirName entered,
                                                    'cloudElementLatLonTRMM':(lat,lon,value) of TRMM data in CE if TRMMdirName entered,
                                                    'TRMMArea': floating-point representing the CE if TRMMdirName entered,
                                                    'CETRMMmax':floating-point representing the max rate in the CE if TRMMdirName entered,
                                                    'CETRMMmin':floating-point representing the min rate in the CE if TRMMdirName entered}
    Assumptions::
            Assumes we are dealing with MERG data which is 4kmx4km resolved, thus the smallest value
            required according to Vila et al. (2008) is 2400km^2
            therefore, 2400/16 = 150 contiguous squares
    '''

    frame = ma.empty((1, mergImgs.shape[1], mergImgs.shape[2]))
    CEcounter = 0
    frameCEcounter = 0
    frameNum = 0
    cloudElementEpsilon = 0.0
    cloudElementDict = {}
    cloudElementCenter = []  # list with two elements [lat,lon] for the center of a CE
    prevFrameCEs = []  # list for CEs in previous frame
    currFrameCEs = []  # list for CEs in current frame
    cloudElementLat = []  # list for a particular CE's lat values
    cloudElementLon = []  # list for a particular CE's lon values
    cloudElementLatLons = []  # list for a particular CE's (lat,lon) values

    prevLatValue = 0.0
    prevLonValue = 0.0
    TIR_min = 0.0
    TIR_max = 0.0
    temporalRes = 3  # TRMM data is 3 hourly
    precipTotal = 0.0
    CETRMMList = []
    precip = []
    TRMMCloudElementLatLons = []

    minCELatLimit = 0.0
    minCELonLimit = 0.0
    maxCELatLimit = 0.0
    maxCELonLimit = 0.0

    nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])

    # openfile for storing ALL cloudElement information
    cloudElementsFile = open(
        (MAINDIRECTORY + '/textFiles/cloudElements.txt'), 'wb')
    # openfile for storing cloudElement information meeting user criteria i.e.
    # MCCs in this case
    cloudElementsUserFile = open(
        (MAINDIRECTORY + '/textFiles/cloudElementsUserFile.txt'), 'w')

    # NB in the TRMM files the info is hours since the time thus 00Z file has
    # in 01, 02 and 03 times
    for t in range(mergImgs.shape[0]):

        #-------------------------------------------------
        # #textfile name for saving the data for arcgis
        # thisFileName = MAINDIRECTORY+'/' + (str(timelist[t])).replace(" ", "_") + '.txt'
        # cloudElementsTextFile = open(thisFileName,'w')
        #-------------------------------------------------

        # determine contiguous locations with temeperature below the warmest
        # temp i.e. cloudElements in each frame
        frame, CEcounter = ndimage.measurements.label(
            mergImgs[t, :, :], structure=STRUCTURING_ELEMENT)
        frameCEcounter = 0
        frameNum += 1

        # for each of the areas identified, check to determine if it a valid CE
        # via an area and T requirement
        for count in range(CEcounter):
            #[0] is time dimension. Determine the actual values from the data
            # loc is a masked array
            try:
                loc = ndimage.find_objects(frame == (count + 1))[0]
            except Exception as e:
                print(("Error is %s" % e))
                continue

            cloudElement = mergImgs[t, :, :][loc]
            labels, lcounter = ndimage.label(cloudElement)

            # determine the true lats and lons for this particular CE
            cloudElementLat = LAT[loc[0], 0]
            cloudElementLon = LON[0, loc[1]]

            # determine number of boxes in this cloudelement
            numOfBoxes = np.count_nonzero(cloudElement)
            cloudElementArea = numOfBoxes * XRES * YRES

            # If the area is greater than the area required, or if the area is smaller than the suggested area, check if it meets a convective fraction requirement
            # consider as CE

            if cloudElementArea >= AREA_MIN or (
                cloudElementArea < AREA_MIN and (
                    (ndimage.minimum(
                        cloudElement,
                        labels=labels)) /
                    float(
                        (ndimage.maximum(
                    cloudElement,
                    labels=labels)))) < CONVECTIVE_FRACTION):

                # get some time information and labeling info
                frameTime = str(timelist[t])
                frameCEcounter += 1
                CEuniqueID = 'F' + str(frameNum) + 'CE' + str(frameCEcounter)

                #-------------------------------------------------
                # textfile name for accesing CE data using MATLAB code
                # thisFileName = MAINDIRECTORY+'/' + (str(timelist[t])).replace(" ", "_") + CEuniqueID +'.txt'
                # cloudElementsTextFile = open(thisFileName,'w')
                #-------------------------------------------------

                # ------ NETCDF File stuff for brightness temp stuff ----------
                thisFileName = MAINDIRECTORY + '/MERGnetcdfCEs/cloudElements' + \
                    (str(timelist[t])).replace(" ", "_") + CEuniqueID + '.nc'
                currNetCDFCEData = Dataset(thisFileName, 'w', format='NETCDF4')
                currNetCDFCEData.description = 'Cloud Element ' + CEuniqueID + ' temperature data'
                currNetCDFCEData.calendar = 'standard'
                currNetCDFCEData.conventions = 'COARDS'
                # dimensions
                currNetCDFCEData.createDimension('time', None)
                currNetCDFCEData.createDimension('lat', len(LAT[:, 0]))
                currNetCDFCEData.createDimension('lon', len(LON[0, :]))
                # variables
                tempDims = ('time', 'lat', 'lon',)
                times = currNetCDFCEData.createVariable(
                    'time', 'f8', ('time',))
                times.units = 'hours since ' + str(timelist[t])[:-6]
                latitudes = currNetCDFCEData.createVariable(
                    'latitude', 'f8', ('lat',))
                longitudes = currNetCDFCEData.createVariable(
                    'longitude', 'f8', ('lon',))
                brightnesstemp = currNetCDFCEData.createVariable(
                    'brightnesstemp', 'i16', tempDims)
                brightnesstemp.units = 'Kelvin'
                # NETCDF data
                dates = [timelist[t] + timedelta(hours=0)]
                times[:] = date2num(dates, units=times.units)
                longitudes[:] = LON[0, :]
                longitudes.units = "degrees_east"
                longitudes.long_name = "Longitude"

                latitudes[:] = LAT[:, 0]
                latitudes.units = "degrees_north"
                latitudes.long_name = "Latitude"

                # generate array of zeros for brightness temperature
                brightnesstemp1 = ma.zeros(
                    (1, len(latitudes), len(longitudes))).astype('int16')
                #-----------End most of NETCDF file stuff ---------------------

                # if other dataset (TRMM) assumed to be a precipitation dataset
                # was entered
                if TRMMdirName:
                    #------------------TRMM stuff -----------------------------
                    fileDate = ((str(timelist[t])).replace(
                        " ", "")[:-8]).replace("-", "")
                    fileHr1 = (str(timelist[t])).replace(" ", "")[-8:-6]

                    if int(fileHr1) % temporalRes == 0:
                        fileHr = fileHr1
                    else:
                        fileHr = (int(fileHr1) / temporalRes) * temporalRes
                    if fileHr < 10:
                        fileHr = '0' + str(fileHr)
                    else:
                        str(fileHr)

                    # open TRMM file for the resolution info and to create the
                    # appropriate sized grid
                    TRMMfileName = TRMMdirName + '/3B42.' + \
                        fileDate + "." + str(fileHr) + ".7A.nc"

                    TRMMData = Dataset(TRMMfileName, 'r', format='NETCDF4')
                    precipRate = TRMMData.variables['pcp'][:, :, :]
                    latsrawTRMMData = TRMMData.variables['latitude'][:]
                    lonsrawTRMMData = TRMMData.variables['longitude'][:]
                    lonsrawTRMMData[lonsrawTRMMData >
                                    180] = lonsrawTRMMData[lonsrawTRMMData > 180] - 360.
                    LONTRMM, LATTRMM = np.meshgrid(
                        lonsrawTRMMData, latsrawTRMMData)

                    nygrdTRMM = len(LATTRMM[:, 0]); nxgrdTRMM = len(
                        LONTRMM[0, :])
                    precipRateMasked = ma.masked_array(
                        precipRate, mask=(precipRate < 0.0))
                    #---------regrid the TRMM data to the MERG dataset --------
                    # regrid using the do_regrid stuff from the Apache OCW
                    regriddedTRMM = ma.zeros((0, nygrd, nxgrd))
                    #regriddedTRMM = process.do_regrid(precipRateMasked[0,:,:], LATTRMM,  LONTRMM, LAT, LON, order=1, mdi= -999999999)
                    regriddedTRMM = do_regrid(
                        precipRateMasked[0, :, :], LATTRMM, LONTRMM, LAT, LON, order=1, mdi=-999999999)
                    #----------------------------------------------------------

                    # #get the lat/lon info from cloudElement
                    # get the lat/lon info from the file
                    latCEStart = LAT[0][0]
                    latCEEnd = LAT[-1][0]
                    lonCEStart = LON[0][0]
                    lonCEEnd = LON[0][-1]

                    # get the lat/lon info for TRMM data (different resolution)
                    latStartT = find_nearest(latsrawTRMMData, latCEStart)
                    latEndT = find_nearest(latsrawTRMMData, latCEEnd)
                    lonStartT = find_nearest(lonsrawTRMMData, lonCEStart)
                    lonEndT = find_nearest(lonsrawTRMMData, lonCEEnd)
                    latStartIndex = np.where(latsrawTRMMData == latStartT)
                    latEndIndex = np.where(latsrawTRMMData == latEndT)
                    lonStartIndex = np.where(lonsrawTRMMData == lonStartT)
                    lonEndIndex = np.where(lonsrawTRMMData == lonEndT)

                    # get the relevant TRMM info
                    CEprecipRate = precipRate[:,
                                              (latStartIndex[0][0] - 1):latEndIndex[0][0],
                                              (lonStartIndex[0][0] - 1):lonEndIndex[0][0]]
                    TRMMData.close()

                    # ------ NETCDF File info for writing TRMM CE rainfall ----
                    thisFileName = MAINDIRECTORY + '/TRMMnetcdfCEs/TRMM' + \
                        (str(timelist[t])).replace(" ", "_") + CEuniqueID + '.nc'
                    currNetCDFTRMMData = Dataset(
                        thisFileName, 'w', format='NETCDF4')
                    currNetCDFTRMMData.description = 'Cloud Element ' + \
                        CEuniqueID + ' precipitation data'
                    currNetCDFTRMMData.calendar = 'standard'
                    currNetCDFTRMMData.conventions = 'COARDS'
                    # dimensions
                    currNetCDFTRMMData.createDimension('time', None)
                    currNetCDFTRMMData.createDimension('lat', len(LAT[:, 0]))
                    currNetCDFTRMMData.createDimension('lon', len(LON[0, :]))

                    # variables
                    TRMMprecip = ('time', 'lat', 'lon',)
                    times = currNetCDFTRMMData.createVariable(
                        'time', 'f8', ('time',))
                    times.units = 'hours since ' + str(timelist[t])[:-6]
                    latitude = currNetCDFTRMMData.createVariable(
                        'latitude', 'f8', ('lat',))
                    longitude = currNetCDFTRMMData.createVariable(
                        'longitude', 'f8', ('lon',))
                    rainFallacc = currNetCDFTRMMData.createVariable(
                        'precipitation_Accumulation', 'f8', TRMMprecip)
                    rainFallacc.units = 'mm'

                    longitude[:] = LON[0, :]
                    longitude.units = "degrees_east"
                    longitude.long_name = "Longitude"

                    latitude[:] = LAT[:, 0]
                    latitude.units = "degrees_north"
                    latitude.long_name = "Latitude"

                    finalCETRMMvalues = ma.zeros((brightnesstemp.shape))
                    #-----------End most of NETCDF file stuff -----------------

                # populate cloudElementLatLons by unpacking the original values from loc to get the actual value for lat and lon
                # TODO: KDW - too dirty... play with itertools.izip or zip and the enumerate with this
                # 			as cloudElement is masked
                for index, value in np.ndenumerate(cloudElement):
                    if value != 0:
                        lat_index, lon_index = index
                        lat_lon_tuple = (
                            cloudElementLat[lat_index],
                            cloudElementLon[lon_index],
                            value)

                        # generate the comma separated file for GIS
                        cloudElementLatLons.append(lat_lon_tuple)

                        # temp data for CE NETCDF file
                        brightnesstemp1[0, int(np.where(LAT[:, 0] == cloudElementLat[lat_index])[0]), int(
                            np.where(LON[0, :] == cloudElementLon[lon_index])[0])] = value

                        if TRMMdirName:
                            finalCETRMMvalues[0, int(np.where(LAT[:, 0] == cloudElementLat[lat_index])[0]), int(np.where(LON[0, :] == cloudElementLon[lon_index])[
                                0])] = regriddedTRMM[int(np.where(LAT[:, 0] == cloudElementLat[lat_index])[0]), int(np.where(LON[0, :] == cloudElementLon[lon_index])[0])]
                            CETRMMList.append((cloudElementLat[lat_index],
                                               cloudElementLon[lon_index],
                                               finalCETRMMvalues[0,
                                                                 cloudElementLat[lat_index],
                                                                 cloudElementLon[lon_index]]))
                brightnesstemp[:] = brightnesstemp1[:]
                currNetCDFCEData.close()

                if TRMMdirName:

                    # calculate the total precip associated with the feature
                    for index, value in np.ndenumerate(finalCETRMMvalues):
                        precipTotal += value
                        precip.append(value)

                    rainFallacc[:] = finalCETRMMvalues[:]
                    currNetCDFTRMMData.close()
                    TRMMnumOfBoxes = np.count_nonzero(finalCETRMMvalues)
                    TRMMArea = TRMMnumOfBoxes * XRES * YRES
                    try:
                        maxCEprecipRate = np.max(
                            finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
                        minCEprecipRate = np.min(
                            finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
                    except BaseException:
                        pass

                # sort cloudElementLatLons by lats
                cloudElementLatLons.sort(key=lambda tup: tup[0])

                # determine if the cloud element the shape
                cloudElementEpsilon = eccentricity(cloudElement)
                cloudElementsUserFile.write(
                    "\n\nTime is: %s" % (str(timelist[t])))
                cloudElementsUserFile.write("\nCEuniqueID is: %s" % CEuniqueID)
                latCenter, lonCenter = ndimage.measurements.center_of_mass(
                    cloudElement, labels=labels)

                # latCenter and lonCenter are given according to the particular array defining this CE
                # so you need to convert this value to the overall domain truth
                latCenter = cloudElementLat[round(latCenter)]
                lonCenter = cloudElementLon[round(lonCenter)]
                cloudElementsUserFile.write(
                    "\nCenter (lat,lon) is: %.2f\t%.2f" %
                    (latCenter, lonCenter))
                cloudElementCenter.append(latCenter)
                cloudElementCenter.append(lonCenter)
                cloudElementsUserFile.write(
                    "\nNumber of boxes are: %d" % numOfBoxes)
                cloudElementsUserFile.write(
                    "\nArea is: %.4f km^2" %
                    (cloudElementArea))
                cloudElementsUserFile.write(
                    "\nAverage brightness temperature is: %.4f K" %
                    ndimage.mean(
                        cloudElement, labels=labels))
                cloudElementsUserFile.write(
                    "\nMin brightness temperature is: %.4f K" %
                    ndimage.minimum(
                        cloudElement, labels=labels))
                cloudElementsUserFile.write(
                    "\nMax brightness temperature is: %.4f K" %
                    ndimage.maximum(
                        cloudElement, labels=labels))
                cloudElementsUserFile.write(
                    "\nBrightness temperature variance is: %.4f K" %
                    ndimage.variance(
                        cloudElement, labels=labels))
                cloudElementsUserFile.write(
                    "\nConvective fraction is: %.4f " %
                    (((ndimage.minimum(
                        cloudElement,
                        labels=labels)) /
                        float(
                        (ndimage.maximum(
                            cloudElement,
                            labels=labels)))) *
                        100.0))
                cloudElementsUserFile.write(
                    "\nEccentricity is: %.4f " %
                    (cloudElementEpsilon))
                # populate the dictionary
                if TRMMdirName:
                    cloudElementDict = {
                        'uniqueID': CEuniqueID,
                        'cloudElementTime': timelist[t],
                        'cloudElementLatLon': cloudElementLatLons,
                        'cloudElementCenter': cloudElementCenter,
                        'cloudElementArea': cloudElementArea,
                        'cloudElementEccentricity': cloudElementEpsilon,
                        'cloudElementTmax': TIR_max,
                        'cloudElementTmin': TIR_min,
                        'cloudElementPrecipTotal': precipTotal,
                        'cloudElementLatLonTRMM': CETRMMList,
                        'TRMMArea': TRMMArea,
                        'CETRMMmax': maxCEprecipRate,
                        'CETRMMmin': minCEprecipRate}
                else:
                    cloudElementDict = {
                        'uniqueID': CEuniqueID,
                        'cloudElementTime': timelist[t],
                        'cloudElementLatLon': cloudElementLatLons,
                        'cloudElementCenter': cloudElementCenter,
                        'cloudElementArea': cloudElementArea,
                        'cloudElementEccentricity': cloudElementEpsilon,
                        'cloudElementTmax': TIR_max,
                        'cloudElementTmin': TIR_min,
                    }

                # current frame list of CEs
                currFrameCEs.append(cloudElementDict)

                # draw the graph node
                CLOUD_ELEMENT_GRAPH.add_node(CEuniqueID, cloudElementDict)

                if frameNum != 1:
                    for cloudElementDict in prevFrameCEs:
                        thisCElen = len(cloudElementLatLons)
                        percentageOverlap, areaOverlap = cloudElementOverlap(
                            cloudElementLatLons, cloudElementDict['cloudElementLatLon'])

                        # change weights to integers because the built in shortest path chokes on floating pts according to Networkx doc
                        # according to Goyens et al, two CEs are considered
                        # related if there is atleast 95% overlap between them
                        # for consecutive imgs a max of 2 hrs apart
                        if percentageOverlap >= 0.95:
                            CLOUD_ELEMENT_GRAPH.add_edge(
                                cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[0])

                        elif percentageOverlap >= 0.90 and percentageOverlap < 0.95:
                            CLOUD_ELEMENT_GRAPH.add_edge(
                                cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[1])

                        elif areaOverlap >= MIN_OVERLAP:
                            CLOUD_ELEMENT_GRAPH.add_edge(
                                cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[2])

                else:
                    # TODO: remove this else as we only wish for the CE details
                    # ensure only the non-zero elements are considered
                    # store intel in allCE file
                    labels, _ = ndimage.label(cloudElement)
                    cloudElementsFile.write(
                        "\n-----------------------------------------------")
                    cloudElementsFile.write(
                        "\n\nTime is: %s" % (str(timelist[t])))
                    # cloudElementLat = LAT[loc[0],0]
                    # cloudElementLon = LON[0,loc[1]]

                    # populate cloudElementLatLons by unpacking the original values from loc
                    # TODO: KDW - too dirty... play with itertools.izip or zip and the enumerate with this
                    # 			as cloudElement is masked
                    for index, value in np.ndenumerate(cloudElement):
                        if value != 0:
                            lat_index, lon_index = index
                            lat_lon_tuple = (
                                cloudElementLat[lat_index],
                                cloudElementLon[lon_index])
                            cloudElementLatLons.append(lat_lon_tuple)

                    cloudElementsFile.write(
                        "\nLocation of rejected CE (lat,lon) points are: %s" %
                        cloudElementLatLons)
                    # latCenter and lonCenter are given according to the particular array defining this CE
                    # so you need to convert this value to the overall domain
                    # truth
                    latCenter, lonCenter = ndimage.measurements.center_of_mass(
                        cloudElement, labels=labels)
                    latCenter = cloudElementLat[round(latCenter)]
                    lonCenter = cloudElementLon[round(lonCenter)]
                    cloudElementsFile.write(
                        "\nCenter (lat,lon) is: %.2f\t%.2f" %
                        (latCenter, lonCenter))
                    cloudElementsFile.write(
                        "\nNumber of boxes are: %d" % numOfBoxes)
                    cloudElementsFile.write(
                        "\nArea is: %.4f km^2" %
                        (cloudElementArea))
                    cloudElementsFile.write(
                        "\nAverage brightness temperature is: %.4f K" %
                        ndimage.mean(
                            cloudElement, labels=labels))
                    cloudElementsFile.write(
                        "\nMin brightness temperature is: %.4f K" %
                        ndimage.minimum(
                            cloudElement, labels=labels))
                    cloudElementsFile.write(
                        "\nMax brightness temperature is: %.4f K" %
                        ndimage.maximum(
                            cloudElement, labels=labels))
                    cloudElementsFile.write(
                        "\nBrightness temperature variance is: %.4f K" %
                        ndimage.variance(
                            cloudElement, labels=labels))
                    cloudElementsFile.write(
                        "\nConvective fraction is: %.4f " %
                        (((ndimage.minimum(
                            cloudElement,
                            labels=labels)) /
                            float(
                            (ndimage.maximum(
                                cloudElement,
                                labels=labels)))) *
                            100.0))
                    cloudElementsFile.write(
                        "\nEccentricity is: %.4f " %
                        (cloudElementEpsilon))
                    cloudElementsFile.write(
                        "\n-----------------------------------------------")

            # reset list for the next CE
            nodeExist = False
            cloudElementCenter = []
            cloudElement = []
            cloudElementLat = []
            cloudElementLon = []
            cloudElementLatLons = []
            brightnesstemp1 = []
            brightnesstemp = []
            finalCETRMMvalues = []
            CEprecipRate = []
            CETRMMList = []
            precipTotal = 0.0
            precip = []
            TRMMCloudElementLatLons = []

        # reset for the next time
        prevFrameCEs = []
        prevFrameCEs = currFrameCEs
        currFrameCEs = []

    cloudElementsFile.close
    cloudElementsUserFile.close
    # if using ARCGIS data store code, uncomment this file close line
    # cloudElementsTextFile.close

    # clean up graph - remove parent and childless nodes
    outAndInDeg = CLOUD_ELEMENT_GRAPH.degree_iter()
    toRemove = [node[0] for node in outAndInDeg if node[1] < 1]
    CLOUD_ELEMENT_GRAPH.remove_nodes_from(toRemove)

    print(("number of nodes are: %s" % CLOUD_ELEMENT_GRAPH.number_of_nodes()))
    print(("number of edges are: %s" % CLOUD_ELEMENT_GRAPH.number_of_edges()))
    print(("*" * 80))

    # hierachial graph output
    graphTitle = "Cloud Elements observed over somewhere from 0000Z to 0000Z"
    #drawGraph(CLOUD_ELEMENT_GRAPH, graphTitle, edgeWeight)

    return CLOUD_ELEMENT_GRAPH
#******************************************************************


def findPrecipRate(TRMMdirName, timelist):
    '''
    Purpose::
            Determines the precipitation rates for MCSs found if TRMMdirName was not entered in findCloudElements this can be used

    Input::
            TRMMdirName: a string representing the directory for the original TRMM netCDF files
            timelist: a list of python datatimes

    Output:: a list of dictionary of the TRMM data
            NB: also creates netCDF with TRMM data for each CE (for post processing) index
                    in MAINDIRECTORY/TRMMnetcdfCEs

    Assumptions:: Assumes that findCloudElements was run without the TRMMdirName value

    '''
    allCEnodesTRMMdata = []
    TRMMdataDict = {}
    precipTotal = 0.0

    os.chdir((MAINDIRECTORY + '/MERGnetcdfCEs/'))
    imgFilename = ''
    temporalRes = 3  # 3 hours for TRMM

    # sort files
    files = list(filter(os.path.isfile, glob.glob("*.nc")))
    files.sort(key=lambda x: os.path.getmtime(x))

    for afile in files:
        fullFname = os.path.splitext(afile)[0]
        noFrameExtension = (fullFname.replace("_", "")).split('F')[0]
        CEuniqueID = 'F' + (fullFname.replace("_", "")).split('F')[1]
        fileDateTimeChar = (noFrameExtension.replace(":", "")).split('s')[1]
        fileDateTime = fileDateTimeChar.replace("-", "")
        fileDate = fileDateTime[:-6]
        fileHr1 = fileDateTime[-6:-4]

        cloudElementData = Dataset(afile, 'r', format='NETCDF4')
        brightnesstemp1 = cloudElementData.variables['brightnesstemp'][:, :, :]
        latsrawCloudElements = cloudElementData.variables['latitude'][:]
        lonsrawCloudElements = cloudElementData.variables['longitude'][:]

        brightnesstemp = np.squeeze(brightnesstemp1, axis=0)

        fileHr = fileHr1 if int(fileHr1) % temporalRes == 0 else (int(fileHr1) / temporalRes) * temporalRes
        fileHr = '0' + str(fileHr) if fileHr < 10 else str(fileHr)

        TRMMfileName = TRMMdirName + "/3B42." + str(fileDate) + "." + fileHr + ".7A.nc"
        TRMMData = Dataset(TRMMfileName, 'r', format='NETCDF4')
        precipRate = TRMMData.variables['pcp'][:, :, :]
        latsrawTRMMData = TRMMData.variables['latitude'][:]
        lonsrawTRMMData = TRMMData.variables['longitude'][:]
        lonsrawTRMMData[lonsrawTRMMData >
                        180] = lonsrawTRMMData[lonsrawTRMMData > 180] - 360.
        LONTRMM, LATTRMM = np.meshgrid(lonsrawTRMMData, latsrawTRMMData)

        #nygrdTRMM = len(LATTRMM[:,0]); nxgrd = len(LONTRMM[0,:])
        nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])

        precipRateMasked = ma.masked_array(precipRate, mask=(precipRate < 0.0))
        #---------regrid the TRMM data to the MERG dataset --------------------
        # regrid using the do_regrid stuff from the Apache OCW
        regriddedTRMM = ma.zeros((0, nygrd, nxgrd))
        regriddedTRMM = do_regrid(
            precipRateMasked[0, :, :], LATTRMM, LONTRMM, LAT, LON, order=1, mdi=-999999999)
        #regriddedTRMM = process.do_regrid(precipRateMasked[0,:,:], LATTRMM,  LONTRMM, LAT, LON, order=1, mdi= -999999999)
        #----------------------------------------------------------------------

        # #get the lat/lon info from
        latCEStart = LAT[0][0]
        latCEEnd = LAT[-1][0]
        lonCEStart = LON[0][0]
        lonCEEnd = LON[0][-1]

        # get the lat/lon info for TRMM data (different resolution)
        latStartT = find_nearest(latsrawTRMMData, latCEStart)
        latEndT = find_nearest(latsrawTRMMData, latCEEnd)
        lonStartT = find_nearest(lonsrawTRMMData, lonCEStart)
        lonEndT = find_nearest(lonsrawTRMMData, lonCEEnd)
        latStartIndex = np.where(latsrawTRMMData == latStartT)
        latEndIndex = np.where(latsrawTRMMData == latEndT)
        lonStartIndex = np.where(lonsrawTRMMData == lonStartT)
        lonEndIndex = np.where(lonsrawTRMMData == lonEndT)

        # get the relevant TRMM info
        CEprecipRate = precipRate[:,
                                  (latStartIndex[0][0] - 1):latEndIndex[0][0],
                                  (lonStartIndex[0][0] - 1):lonEndIndex[0][0]]
        TRMMData.close()

        # ------ NETCDF File stuff ------------------------------------
        thisFileName = MAINDIRECTORY + '/TRMMnetcdfCEs/' + \
            fileDateTime + CEuniqueID + '.nc'
        currNetCDFTRMMData = Dataset(thisFileName, 'w', format='NETCDF4')
        currNetCDFTRMMData.description = 'Cloud Element ' + CEuniqueID + ' rainfall data'
        currNetCDFTRMMData.calendar = 'standard'
        currNetCDFTRMMData.conventions = 'COARDS'
        # dimensions
        currNetCDFTRMMData.createDimension('time', None)
        currNetCDFTRMMData.createDimension('lat', len(LAT[:, 0]))
        currNetCDFTRMMData.createDimension('lon', len(LON[0, :]))
        # variables
        TRMMprecip = ('time', 'lat', 'lon',)
        times = currNetCDFTRMMData.createVariable('time', 'f8', ('time',))
        times.units = 'hours since ' + fileDateTime[:-6]
        latitude = currNetCDFTRMMData.createVariable(
            'latitude', 'f8', ('lat',))
        longitude = currNetCDFTRMMData.createVariable(
            'longitude', 'f8', ('lon',))
        rainFallacc = currNetCDFTRMMData.createVariable(
            'precipitation_Accumulation', 'f8', TRMMprecip)
        rainFallacc.units = 'mm'

        longitude[:] = LON[0, :]
        longitude.units = "degrees_east"
        longitude.long_name = "Longitude"

        latitude[:] = LAT[:, 0]
        latitude.units = "degrees_north"
        latitude.long_name = "Latitude"

        finalCETRMMvalues = ma.zeros((brightnesstemp1.shape))
        #-----------End most of NETCDF file stuff -----------------------------
        for index, value in np.ndenumerate(brightnesstemp):
            lat_index, lon_index = index
            currTimeValue = 0
            if value > 0:

                finalCETRMMvalues[0, lat_index, lon_index] = regriddedTRMM[int(np.where(
                    LAT[:, 0] == LAT[lat_index, 0])[0]), int(np.where(LON[0, :] == LON[0, lon_index])[0])]

        rainFallacc[:] = finalCETRMMvalues
        currNetCDFTRMMData.close()

        for index, value in np.ndenumerate(finalCETRMMvalues):
            precipTotal += value

        TRMMnumOfBoxes = np.count_nonzero(finalCETRMMvalues)
        TRMMArea = TRMMnumOfBoxes * XRES * YRES

        try:
            minCEprecipRate = np.min(
                finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
        except BaseException:
            minCEprecipRate = 0.0

        try:
            maxCEprecipRate = np.max(
                finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
        except BaseException:
            maxCEprecipRate = 0.0

        # add info to CLOUDELEMENTSGRAPH
        # TODO try block
        for eachdict in CLOUD_ELEMENT_GRAPH.nodes(CEuniqueID):
            if eachdict[1]['uniqueID'] == CEuniqueID:
                if 'cloudElementPrecipTotal' not in list(eachdict[1].keys()):
                    eachdict[1]['cloudElementPrecipTotal'] = precipTotal
                if 'cloudElementLatLonTRMM' not in list(eachdict[1].keys()):
                    eachdict[1]['cloudElementLatLonTRMM'] = finalCETRMMvalues
                if 'TRMMArea' not in list(eachdict[1].keys()):
                    eachdict[1]['TRMMArea'] = TRMMArea
                if 'CETRMMmin' not in list(eachdict[1].keys()):
                    eachdict[1]['CETRMMmin'] = minCEprecipRate
                if 'CETRMMmax' not in list(eachdict[1].keys()):
                    eachdict[1]['CETRMMmax'] = maxCEprecipRate

        # clean up
        precipTotal = 0.0
        latsrawTRMMData = []
        lonsrawTRMMData = []
        latsrawCloudElements = []
        lonsrawCloudElements = []
        finalCETRMMvalues = []
        CEprecipRate = []
        brightnesstemp = []
        TRMMdataDict = {}

    return allCEnodesTRMMdata


def findCloudClusters(CEGraph):
    '''
    Purpose::
            Determines the cloud clusters properties from the subgraphs in
            the graph i.e. prunes the graph according to the minimum depth

    Input::
            CEGraph: a Networkx directed graph of the CEs with weighted edges
            according the area overlap between nodes (CEs) of consectuive frames

    Output::
            PRUNED_GRAPH: a Networkx directed graph of with CCs/ MCSs
    '''

    seenNode = []
    allMCSLists = []
    pathDictList = []
    pathList = []

    cloudClustersFile = open(
        (MAINDIRECTORY + '/textFiles/cloudClusters.txt'), 'wb')

    for eachNode in CEGraph:
        # check if the node has been seen before
        if eachNode not in dict(enumerate(zip(*seenNode))):
            # look for all trees associated with node as the root
            thisPathDistanceAndLength = nx.single_source_dijkstra(
                CEGraph, eachNode)
            # determine the actual shortestPath and minimum depth/length
            maxDepthAndMinPath = findMaxDepthAndMinPath(
                thisPathDistanceAndLength)
            if maxDepthAndMinPath:
                maxPathLength = maxDepthAndMinPath[0]
                shortestPath = maxDepthAndMinPath[1]

                # add nodes and paths to PRUNED_GRAPH
                for i in range(len(shortestPath)):
                    if PRUNED_GRAPH.has_node(shortestPath[i]) is False:
                        PRUNED_GRAPH.add_node(shortestPath[i])

                    # add edge if necessary
                    if i < (len(shortestPath) - 1) and PRUNED_GRAPH.has_edge(
                            shortestPath[i], shortestPath[i + 1]) is False:
                        prunedGraphEdgeweight = CEGraph.get_edge_data(
                            shortestPath[i], shortestPath[i + 1])['weight']
                        PRUNED_GRAPH.add_edge(
                            shortestPath[i], shortestPath[i + 1], weight=prunedGraphEdgeweight)

                # note information in a file for consideration later i.e.
                # checking to see if it works
                cloudClustersFile.write(
                    "\nSubtree pathlength is %d and path is %s" %
                    (maxPathLength, shortestPath))
                # update seenNode info
                seenNode.append(shortestPath)

    print("pruned graph")
    print("number of nodes are: %s", PRUNED_GRAPH.number_of_nodes())
    print("number of edges are: %s", PRUNED_GRAPH.number_of_edges())
    print("*" * 80)

    graphTitle = "Cloud Clusters observed over somewhere during sometime"
    #drawGraph(PRUNED_GRAPH, graphTitle, edgeWeight)
    cloudClustersFile.close

    return PRUNED_GRAPH
#******************************************************************


def findMCC(prunedGraph):
    '''
    Purpose::
            Determines if subtree is a MCC according to Laurent et al 1998 criteria

    Input::
            prunedGraph: a Networkx Graph representing the CCs

    Output::
            finalMCCList: a list of list of tuples representing a MCC

    Assumptions:
            frames are ordered and are equally distributed in time e.g. hrly satellite images

    '''
    MCCList = []
    MCSList = []
    definiteMCC = []
    definiteMCS = []
    eachList = []
    eachMCCList = []
    maturing = False
    decaying = False
    fNode = ''
    lNode = ''
    removeList = []
    imgCount = 0
    imgTitle = ''

    maxShieldNode = ''
    orderedPath = []
    treeTraversalList = []
    definiteMCCFlag = False
    unDirGraph = nx.Graph()
    aSubGraph = nx.DiGraph()
    definiteMCSFlag = False

    # connected_components is not available for DiGraph, so generate graph as
    # undirected
    unDirGraph = PRUNED_GRAPH.to_undirected()
    subGraph = nx.connected_component_subgraphs(unDirGraph)

    # for each path in the subgraphs determined
    for path in subGraph:
        # definite is a subTree provided the duration is longer than 3 hours

        if len(path.nodes()) > MIN_MCS_DURATION:
            orderedPath = path.nodes()
            orderedPath.sort(key=lambda item: (
                len(item.split('C')[0]), item.split('C')[0]))
            # definiteMCS.append(orderedPath)

            # build back DiGraph for checking purposes/paper purposes
            aSubGraph.add_nodes_from(path.nodes())
            for eachNode in path.nodes():
                if prunedGraph.predecessors(eachNode):
                    for node in prunedGraph.predecessors(eachNode):
                        aSubGraph.add_edge(
                            node, eachNode, weight=edgeWeight[0])

                if prunedGraph.successors(eachNode):
                    for node in prunedGraph.successors(eachNode):
                        aSubGraph.add_edge(
                            eachNode, node, weight=edgeWeight[0])
            imgTitle = 'CC' + str(imgCount + 1)
            # drawGraph(aSubGraph, imgTitle, edgeWeight) #for eachNode in path:
            imgCount += 1
            #----------end build back -----------------------------------------

            mergeList, splitList = hasMergesOrSplits(path)
            # add node behavior regarding neutral, merge, split or both
            for node in path:
                if node in mergeList and node in splitList:
                    addNodeBehaviorIdentifier(node, 'B')
                elif node in mergeList and node not in splitList:
                    addNodeBehaviorIdentifier(node, 'M')
                elif node in splitList and node not in mergeList:
                    addNodeBehaviorIdentifier(node, 'S')
                else:
                    addNodeBehaviorIdentifier(node, 'N')

            # Do the first part of checking for the MCC feature
            # find the path
            treeTraversalList = traverseTree(aSubGraph, orderedPath[0], [], [])
            #print("treeTraversalList is %s" % treeTraversalList)
            # check the nodes to determine if a MCC on just the area criteria
            # (consecutive nodes meeting the area and temp requirements)
            MCCList = checkedNodesMCC(prunedGraph, treeTraversalList)
            for aDict in MCCList:
                for eachNode in aDict["fullMCSMCC"]:
                    addNodeMCSIdentifier(eachNode[0], eachNode[1])

            # do check for if MCCs overlap
            if MCCList:
                if len(MCCList) > 1:
                    # for eachDict in MCCList:
                    for count in range(len(MCCList)):
                        # if there are more than two lists
                        if count >= 1:
                            # and the first node in this list
                            eachList = list(
                                x[0] for x in MCCList[count]["possMCCList"])
                            eachList.sort(key=lambda nodeID: (
                                len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                            if eachList:
                                fNode = eachList[0]
                                # get the lastNode in the previous possMCC list
                                eachList = list(
                                    x[0] for x in MCCList[(count - 1)]["possMCCList"])
                                eachList.sort(key=lambda nodeID: (
                                    len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                                if eachList:
                                    lNode = eachList[-1]
                                    if lNode in CLOUD_ELEMENT_GRAPH.predecessors(
                                            fNode):
                                        for aNode in CLOUD_ELEMENT_GRAPH.predecessors(
                                                fNode):
                                            if aNode in eachList and aNode == lNode:
                                                                                                # if
                                                                                                # edge_data
                                                                                                # is
                                                                                                # equal
                                                                                                # or
                                                                                                # less
                                                                                                # than
                                                                                                # to
                                                                                                # the
                                                                                                # exisitng
                                                                                                # edge
                                                                                                # in
                                                                                                # the
                                                                                                # tree
                                                                                                # append
                                                                                                # one
                                                                                                # to
                                                                                                # the
                                                                                                # other
                                                if CLOUD_ELEMENT_GRAPH.get_edge_data(
                                                        aNode, fNode)['weight'] <= CLOUD_ELEMENT_GRAPH.get_edge_data(
                                                        lNode, fNode)['weight']:
                                                    MCCList[count - 1]["possMCCList"].extend(
                                                        MCCList[count]["possMCCList"])
                                                    MCCList[count - 1]["fullMCSMCC"].extend(
                                                        MCCList[count]["fullMCSMCC"])
                                                    MCCList[count -
                                                            1]["durationAandB"] += MCCList[count]["durationAandB"]
                                                    MCCList[count -
                                                            1]["CounterCriteriaA"] += MCCList[count]["CounterCriteriaA"]
                                                    MCCList[count -
                                                            1]["highestMCCnode"] = MCCList[count]["highestMCCnode"]
                                                    MCCList[count -
                                                            1]["frameNum"] = MCCList[count]["frameNum"]
                                                    removeList.append(count)
                # update the MCCList
                if removeList:
                    for i in removeList:
                        if (len(MCCList) - 1) > i:
                            del MCCList[i]
                            removeList = []

            # check if the nodes also meet the duration criteria and the shape
            # crieria
            for eachDict in MCCList:
                # order the fullMCSMCC list, then run maximum extent and
                # eccentricity criteria
                if (eachDict["durationAandB"] *
                    TRES) >= MINIMUM_DURATION and (eachDict["durationAandB"] *
                                                   TRES) <= MAXIMUM_DURATION:
                    eachList = list(x[0] for x in eachDict["fullMCSMCC"])
                    eachList.sort(key=lambda nodeID: (
                        len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                    eachMCCList = list(x[0] for x in eachDict["possMCCList"])
                    eachMCCList.sort(key=lambda nodeID: (
                        len(nodeID.split('C')[0]), nodeID.split('C')[0]))

                    # update the nodemcsidentifer behavior
                    # find the first element eachMCCList in eachList, and ensure everything ahead of it is indicated as 'I',
                    # find last element in eachMCCList in eachList and ensure everything after it is indicated as 'D'
                    # ensure that everything between is listed as 'M'
                    for eachNode in eachList[:(
                            eachList.index(eachMCCList[0]))]:
                        addNodeMCSIdentifier(eachNode, 'I')

                    addNodeMCSIdentifier(eachMCCList[0], 'M')

                    for eachNode in eachList[(
                            eachList.index(eachMCCList[-1]) + 1):]:
                        addNodeMCSIdentifier(eachNode, 'D')

                    # update definiteMCS list
                    for eachNode in orderedPath[(
                            orderedPath.index(eachMCCList[-1]) + 1):]:
                        addNodeMCSIdentifier(eachNode, 'D')

                    # run maximum extent and eccentricity criteria
                    maxExtentNode, definiteMCCFlag = maxExtentAndEccentricity(
                        eachList)
                    if definiteMCCFlag:
                        definiteMCC.append(eachList)

            definiteMCS.append(orderedPath)

            # reset for next subGraph
            aSubGraph.clear()
            orderedPath = []
            MCCList = []
            MCSList = []
            definiteMCSFlag = False

    return definiteMCC, definiteMCS
#******************************************************************


def traverseTree(subGraph, node, stack, checkedNodes=None):
    '''
    Purpose::
            To traverse a tree using a modified depth-first iterative deepening (DFID) search algorithm

    Input::
            subGraph: a Networkx DiGraph representing a CC
                    lengthOfsubGraph: an integer representing the length of the subgraph
                    node: a string representing the node currently being checked
                    stack: a list of strings representing a list of nodes in a stack functionality
                                    i.e. Last-In-First-Out (LIFO) for sorting the information from each visited node
                    checkedNodes: a list of strings representing the list of the nodes in the traversal

    Output::
            checkedNodes: a list of strings representing the list of the nodes in the traversal

    Assumptions:
            frames are ordered and are equally distributed in time e.g. hrly satellite images
    '''
    if len(checkedNodes) == len(subGraph):
        return checkedNodes

    if not checkedNodes:
        stack = []
        checkedNodes.append(node)

    # check one level infront first...if something does exisit, stick it at
    # the front of the stack
    upOneLevel = subGraph.predecessors(node)
    downOneLevel = subGraph.successors(node)
    for parent in upOneLevel:
        if parent not in checkedNodes and parent not in stack:
            for child in downOneLevel:
                if child not in checkedNodes and child not in stack:
                    stack.insert(0, child)

            stack.insert(0, parent)
    for child in downOneLevel:
        if child not in checkedNodes and child not in stack:
            if len(subGraph.predecessors(child)) > 1 or node in checkedNodes:
                stack.insert(0, child)
            else:
                stack.append(child)

    for eachNode in stack:
        if eachNode not in checkedNodes:
            checkedNodes.append(eachNode)
            return traverseTree(subGraph, eachNode, stack, checkedNodes)

    return checkedNodes


def findMCC(prunedGraph):
    '''
    Purpose::
            Determines if subtree is a MCC according to Laurent et al 1998 criteria

    Input::
            prunedGraph: a Networkx Graph representing the CCs

    Output::
            finalMCCList: a list of list of tuples representing a MCC

    Assumptions:
            frames are ordered and are equally distributed in time e.g. hrly satellite images

    '''
    MCCList = []
    MCSList = []
    definiteMCC = []
    definiteMCS = []
    eachList = []
    eachMCCList = []
    maturing = False
    decaying = False
    fNode = ''
    lNode = ''
    removeList = []
    imgCount = 0
    imgTitle = ''

    maxShieldNode = ''
    orderedPath = []
    treeTraversalList = []
    definiteMCCFlag = False
    unDirGraph = nx.Graph()
    aSubGraph = nx.DiGraph()
    definiteMCSFlag = False

    # connected_components is not available for DiGraph, so generate graph as
    # undirected
    unDirGraph = PRUNED_GRAPH.to_undirected()
    subGraph = nx.connected_component_subgraphs(unDirGraph)

    # for each path in the subgraphs determined
    for path in subGraph:
                # definite is a subTree provided the duration is longer than 3
                # hours

        if len(path.nodes()) > MIN_MCS_DURATION:
            orderedPath = path.nodes()
            orderedPath.sort(key=lambda item: (
                len(item.split('C')[0]), item.split('C')[0]))
            # definiteMCS.append(orderedPath)

            # build back DiGraph for checking purposes/paper purposes
            aSubGraph.add_nodes_from(path.nodes())
            for eachNode in path.nodes():
                if prunedGraph.predecessors(eachNode):
                    for node in prunedGraph.predecessors(eachNode):
                        aSubGraph.add_edge(
                            node, eachNode, weight=edgeWeight[0])

                if prunedGraph.successors(eachNode):
                    for node in prunedGraph.successors(eachNode):
                        aSubGraph.add_edge(
                            eachNode, node, weight=edgeWeight[0])
            imgTitle = 'CC' + str(imgCount + 1)
            # drawGraph(aSubGraph, imgTitle, edgeWeight) #for eachNode in path:
            imgCount += 1
            #----------end build back -----------------------------------------

            mergeList, splitList = hasMergesOrSplits(path)
            # add node behavior regarding neutral, merge, split or both
            for node in path:
                if node in mergeList and node in splitList:
                    addNodeBehaviorIdentifier(node, 'B')
                elif node in mergeList and node not in splitList:
                    addNodeBehaviorIdentifier(node, 'M')
                elif node in splitList and node not in mergeList:
                    addNodeBehaviorIdentifier(node, 'S')
                else:
                    addNodeBehaviorIdentifier(node, 'N')

            # Do the first part of checking for the MCC feature
            # find the path
            treeTraversalList = traverseTree(
                aSubGraph, orderedPath[0], [], set(), [])
            # print "treeTraversalList is ", treeTraversalList
            # check the nodes to determine if a MCC on just the area criteria
            # (consecutive nodes meeting the area and temp requirements)
            MCCList = checkedNodesMCC(prunedGraph, treeTraversalList)
            for aDict in MCCList:
                for eachNode in aDict["fullMCSMCC"]:
                    addNodeMCSIdentifier(eachNode[0], eachNode[1])

            # do check for if MCCs overlap
            if MCCList:
                if len(MCCList) > 1:
                    # for eachDict in MCCList:
                    for count in range(len(MCCList)):
                        # if there are more than two lists
                        if count >= 1:
                            # and the first node in this list
                            eachList = list(
                                x[0] for x in MCCList[count]["possMCCList"])
                            eachList.sort(key=lambda nodeID: (
                                len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                            if eachList:
                                fNode = eachList[0]
                                # get the lastNode in the previous possMCC list
                                eachList = list(
                                    x[0] for x in MCCList[(count - 1)]["possMCCList"])
                                eachList.sort(key=lambda nodeID: (
                                    len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                                if eachList:
                                    lNode = eachList[-1]
                                    if lNode in CLOUD_ELEMENT_GRAPH.predecessors(
                                            fNode):
                                        for aNode in CLOUD_ELEMENT_GRAPH.predecessors(
                                                fNode):
                                            if aNode in eachList and aNode == lNode:
                                                                                                # if
                                                                                                # edge_data
                                                                                                # is
                                                                                                # equal
                                                                                                # or
                                                                                                # less
                                                                                                # than
                                                                                                # to
                                                                                                # the
                                                                                                # exisitng
                                                                                                # edge
                                                                                                # in
                                                                                                # the
                                                                                                # tree
                                                                                                # append
                                                                                                # one
                                                                                                # to
                                                                                                # the
                                                                                                # other
                                                if CLOUD_ELEMENT_GRAPH.get_edge_data(
                                                        aNode, fNode)['weight'] <= CLOUD_ELEMENT_GRAPH.get_edge_data(
                                                        lNode, fNode)['weight']:
                                                    MCCList[count - 1]["possMCCList"].extend(
                                                        MCCList[count]["possMCCList"])
                                                    MCCList[count - 1]["fullMCSMCC"].extend(
                                                        MCCList[count]["fullMCSMCC"])
                                                    MCCList[count - 1]["durationAandB"] += MCCList[count]["durationAandB"]
                                                    MCCList[count -
                                                            1]["CounterCriteriaA"] += MCCList[count]["CounterCriteriaA"]
                                                    MCCList[count -
                                                            1]["highestMCCnode"] = MCCList[count]["highestMCCnode"]
                                                    MCCList[count - 1]["frameNum"] = MCCList[count]["frameNum"]
                                                    removeList.append(count)
                # update the MCCList
                if removeList:
                    for i in removeList:
                        if (len(MCCList) - 1) > i:
                            del MCCList[i]
                            removeList = []

            # check if the nodes also meet the duration criteria and the shape
            # crieria
            for eachDict in MCCList:
                # order the fullMCSMCC list, then run maximum extent and
                # eccentricity criteria
                if (eachDict["durationAandB"] *
                    TRES) >= MINIMUM_DURATION and (eachDict["durationAandB"] *
                                                   TRES) <= MAXIMUM_DURATION:
                    eachList = list(x[0] for x in eachDict["fullMCSMCC"])
                    eachList.sort(key=lambda nodeID: (
                        len(nodeID.split('C')[0]), nodeID.split('C')[0]))
                    eachMCCList = list(x[0] for x in eachDict["possMCCList"])
                    eachMCCList.sort(key=lambda nodeID: (
                        len(nodeID.split('C')[0]), nodeID.split('C')[0]))

                    # update the nodemcsidentifer behavior
                    # find the first element eachMCCList in eachList, and ensure everything ahead of it is indicated as 'I',
                    # find last element in eachMCCList in eachList and ensure everything after it is indicated as 'D'
                    # ensure that everything between is listed as 'M'
                    for eachNode in eachList[:(
                            eachList.index(eachMCCList[0]))]:
                        addNodeMCSIdentifier(eachNode, 'I')

                    addNodeMCSIdentifier(eachMCCList[0], 'M')

                    for eachNode in eachList[(
                            eachList.index(eachMCCList[-1]) + 1):]:
                        addNodeMCSIdentifier(eachNode, 'D')

                    # update definiteMCS list
                    for eachNode in orderedPath[(
                            orderedPath.index(eachMCCList[-1]) + 1):]:
                        addNodeMCSIdentifier(eachNode, 'D')

                    # run maximum extent and eccentricity criteria
                    maxExtentNode, definiteMCCFlag = maxExtentAndEccentricity(
                        eachList)
                    # print "maxExtentNode, definiteMCCFlag ", maxExtentNode,
                    # definiteMCCFlag
                    if definiteMCCFlag:
                        definiteMCC.append(eachList)

            definiteMCS.append(orderedPath)

            # reset for next subGraph
            aSubGraph.clear()
            orderedPath = []
            MCCList = []
            MCSList = []
            definiteMCSFlag = False

    return definiteMCC, definiteMCS
#******************************************************************


def traverseTree(subGraph, node, stack, bookkeeper_stack, checkedNodes=None):
    '''
    Purpose::
            To traverse a tree using a modified depth-first iterative deepening (DFID) search algorithm

    Input::
            subGraph: a Networkx DiGraph representing a CC
                    lengthOfsubGraph: an integer representing the length of the subgraph
                    node: a string representing the node currently being checked
                    stack: a list of strings representing a list of nodes in a stack functionality
                                    i.e. Last-In-First-Out (LIFO) for sorting the information from each visited node
                    checkedNodes: a list of strings representing the list of the nodes in the traversal

    Output::
            checkedNodes: a list of strings representing the list of the nodes in the traversal

    Assumptions:
            frames are ordered and are equally distributed in time e.g. hrly satellite images

    '''
    if len(checkedNodes) == len(subGraph):
        return checkedNodes

    if not checkedNodes:
        stack = []
        bookkeeper_stack = set()
        checkedNodes.append(node)

    # check one level infront first...if something does exisit, stick it at
    # the front of the stack
    upOneLevel = subGraph.predecessors(node)
    downOneLevel = subGraph.successors(node)
    for parent in upOneLevel:
        if parent not in checkedNodes and parent not in bookkeeper_stack:
            for child in downOneLevel:
                if child not in checkedNodes and child not in bookkeeper_stack:
                    stack.insert(0, child)
                    bookkeeper_stack.add(child)
            stack.insert(0, parent)
            bookkeeper_stack.add(parent)

    for child in downOneLevel:
        if child not in checkedNodes and child not in bookkeeper_stack:
            stack.insert(0, child)
            bookkeeper_stack.add(child)

    for eachNode in stack:
        if eachNode not in checkedNodes:
            checkedNodes.append(eachNode)
            return traverseTree(
                subGraph,
                eachNode,
                stack,
                bookkeeper_stack,
                checkedNodes)

    return checkedNodes
#******************************************************************


def checkedNodesMCC(prunedGraph, nodeList):
    '''
    Purpose ::
            Determine if this path is (or is part of) a MCC and provides
            preliminary information regarding the stages of the feature

    Input::
            prunedGraph: a Networkx Graph representing all the cloud clusters
            nodeList: list of strings (CE ID) from the traversal

    Output::
            potentialMCCList: list of dictionaries representing all possible MCC within the path
                    dictionary = {"possMCCList":[(node,'I')], "fullMCSMCC":[(node,'I')], "CounterCriteriaA": CounterCriteriaA, "durationAandB": durationAandB}
    '''

    CounterCriteriaAFlag = False
    CounterCriteriaBFlag = False
    INITIATIONFLAG = False
    MATURITYFLAG = False
    DECAYFLAG = False
    thisdict = {}  # will have the same items as the cloudElementDict
    cloudElementAreaB = 0.0
    cloudElementAreaA = 0.0
    epsilon = 0.0
    frameNum = 0
    oldNode = ''
    potentialMCCList = []
    durationAandB = 0

    # check for if the list contains only one string/node
    if isinstance(nodeList, str):
        oldNode = nodeList
        nodeList = []
        nodeList.append(oldNode)

    for node in nodeList:
        thisdict = thisDict(node)
        CounterCriteriaAFlag = False
        CounterCriteriaBFlag = False
        existingFrameFlag = False

        if thisdict['cloudElementArea'] >= OUTER_CLOUD_SHIELD_AREA:
            CounterCriteriaAFlag = True
            INITIATIONFLAG = True
            MATURITYFLAG = False

            # check if criteriaA is met
            cloudElementAreaA, criteriaA = checkCriteria(
                thisdict['cloudElementLatLon'], OUTER_CLOUD_SHIELD_TEMPERATURE)
            # TODO: calcuate the eccentricity at this point and read over????or
            # create a new field in the dict

            if cloudElementAreaA >= OUTER_CLOUD_SHIELD_AREA:
                # check if criteriaB is met
                cloudElementAreaB, criteriaB = checkCriteria(
                    thisdict['cloudElementLatLon'], INNER_CLOUD_SHIELD_TEMPERATURE)

                # if Criteria A and B have been met, then the MCC is initiated,
                # i.e. store node as potentialMCC
                if cloudElementAreaB >= INNER_CLOUD_SHIELD_AREA:
                    # TODO: add another field to the dictionary for the
                    # OUTER_AREA_SHIELD area
                    CounterCriteriaBFlag = True
                    # append this information on to the dictionary
                    addInfothisDict(node, cloudElementAreaB, criteriaB)
                    INITIATIONFLAG = False
                    MATURITYFLAG = True
                    stage = 'M'
                    potentialMCCList = updateMCCList(
                        prunedGraph,
                        potentialMCCList,
                        node,
                        stage,
                        CounterCriteriaAFlag,
                        CounterCriteriaBFlag)
                else:
                    # criteria B failed
                    CounterCriteriaBFlag = False
                    if INITIATIONFLAG:
                        stage = 'I'
                        potentialMCCList = updateMCCList(
                            prunedGraph,
                            potentialMCCList,
                            node,
                            stage,
                            CounterCriteriaAFlag,
                            CounterCriteriaBFlag)

                    elif (INITIATIONFLAG == False and MATURITYFLAG == True) or DECAYFLAG == True:
                        DECAYFLAG = True
                        MATURITYFLAG = False
                        stage = 'D'
                        potentialMCCList = updateMCCList(
                            prunedGraph,
                            potentialMCCList,
                            node,
                            stage,
                            CounterCriteriaAFlag,
                            CounterCriteriaBFlag)
            else:
                # criteria A failed
                CounterCriteriaAFlag = False
                CounterCriteriaBFlag = False
                # add as a CE before or after the main feature
                if INITIATIONFLAG or (
                        INITIATIONFLAG == False and MATURITYFLAG == True):
                    stage = "I"
                    potentialMCCList = updateMCCList(
                        prunedGraph,
                        potentialMCCList,
                        node,
                        stage,
                        CounterCriteriaAFlag,
                        CounterCriteriaBFlag)
                elif (INITIATIONFLAG == False and MATURITYFLAG == False) or DECAYFLAG == True:
                    stage = "D"
                    DECAYFLAG = True
                    potentialMCCList = updateMCCList(
                        prunedGraph,
                        potentialMCCList,
                        node,
                        stage,
                        CounterCriteriaAFlag,
                        CounterCriteriaBFlag)
                elif (INITIATIONFLAG == False and MATURITYFLAG == False and DECAYFLAG == False):
                    stage = "I"
                    potentialMCCList = updateMCCList(
                        prunedGraph,
                        potentialMCCList,
                        node,
                        stage,
                        CounterCriteriaAFlag,
                        CounterCriteriaBFlag)

        else:
            # criteria A failed
            CounterCriteriaAFlag = False
            CounterCriteriaBFlag = False
            # add as a CE before or after the main feature
            if INITIATIONFLAG or (
                    INITIATIONFLAG == False and MATURITYFLAG == True):
                stage = "I"
                potentialMCCList = updateMCCList(
                    prunedGraph,
                    potentialMCCList,
                    node,
                    stage,
                    CounterCriteriaAFlag,
                    CounterCriteriaBFlag)
            elif (INITIATIONFLAG == False and MATURITYFLAG == False) or DECAYFLAG == True:
                stage = "D"
                DECAYFLAG = True
                potentialMCCList = updateMCCList(
                    prunedGraph,
                    potentialMCCList,
                    node,
                    stage,
                    CounterCriteriaAFlag,
                    CounterCriteriaBFlag)
            elif (INITIATIONFLAG == False and MATURITYFLAG == False and DECAYFLAG == False):
                stage = "I"
                potentialMCCList = updateMCCList(
                    prunedGraph,
                    potentialMCCList,
                    node,
                    stage,
                    CounterCriteriaAFlag,
                    CounterCriteriaBFlag)

    return potentialMCCList
#******************************************************************


def updateMCCList(
        prunedGraph,
        potentialMCCList,
        node,
        stage,
        CounterCriteriaAFlag,
        CounterCriteriaBFlag):
    '''
    Purpose::
            Utility function to determine if a path is (or is part of) a MCC and provides
                       preliminary information regarding the stages of the feature

    Input::
            prunedGraph: a Networkx Graph representing all the cloud clusters
            potentialMCCList: a list of dictionaries representing the possible MCCs within a path
            node: a string representing the cloud element currently being assessed
            CounterCriteriaAFlag: a boolean value indicating whether the node meets the MCC criteria A according to Laurent et al
            CounterCriteriaBFlag: a boolean value indicating whether the node meets the MCC criteria B according to Laurent et al

    Output::
            potentialMCCList: list of dictionaries representing all possible MCC within the path
                     dictionary = {"possMCCList":[(node,'I')], "fullMCSMCC":[(node,'I')], "CounterCriteriaA": CounterCriteriaA, "durationAandB": durationAandB}

    '''
    existingFrameFlag = False
    existingMCSFrameFlag = False
    predecessorsFlag = False
    predecessorsMCSFlag = False
    successorsFlag = False
    successorsMCSFlag = False
    frameNum = 0

    frameNum = int((node.split('CE')[0]).split('F')[1])
    if potentialMCCList == []:
        # list empty
        stage = 'I'
        if CounterCriteriaAFlag and CounterCriteriaBFlag:
            potentialMCCList.append(
                {
                    "possMCCList": [
                        (node,
                         stage)],
                    "fullMCSMCC": [
                        (node,
                         stage)],
                    "CounterCriteriaA": 1,
                    "durationAandB": 1,
                    "highestMCCnode": node,
                    "frameNum": frameNum})
        elif CounterCriteriaAFlag and CounterCriteriaBFlag == False:
            potentialMCCList.append({"possMCCList": [],
                                     "fullMCSMCC": [(node,
                                                     stage)],
                                     "CounterCriteriaA": 1,
                                     "durationAandB": 0,
                                     "highestMCCnode": "",
                                     "frameNum": 0})
        elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
            potentialMCCList.append({"possMCCList": [],
                                     "fullMCSMCC": [(node,
                                                     stage)],
                                     "CounterCriteriaA": 0,
                                     "durationAandB": 0,
                                     "highestMCCnode": "",
                                     "frameNum": 0})

    else:
        # list not empty
        predecessorsFlag, index = isThereALink(
            prunedGraph, 1, node, potentialMCCList, 1)

        if predecessorsFlag:

            for eachNode in potentialMCCList[index]["possMCCList"]:
                if int((eachNode[0].split('CE')[0]).split('F')[1]) == frameNum:
                    existingFrameFlag = True

            # this MUST come after the check for the existing frame
            if CounterCriteriaAFlag and CounterCriteriaBFlag:
                stage = 'M'
                potentialMCCList[index]["possMCCList"].append((node, stage))
                potentialMCCList[index]["fullMCSMCC"].append((node, stage))

            if not existingFrameFlag:
                if CounterCriteriaAFlag and CounterCriteriaBFlag:
                    stage = 'M'
                    potentialMCCList[index]["CounterCriteriaA"] += 1
                    potentialMCCList[index]["durationAandB"] += 1
                    if frameNum > potentialMCCList[index]["frameNum"]:
                        potentialMCCList[index]["frameNum"] = frameNum
                        potentialMCCList[index]["highestMCCnode"] = node
                    return potentialMCCList

                # if this frameNum doesn't exist and this frameNum is less than
                # the MCC node max frame Num (including 0), then append to
                # fullMCSMCC list
                if frameNum > potentialMCCList[index]["frameNum"] or potentialMCCList[index]["frameNum"] == 0:
                    stage = 'I'
                    if CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                        potentialMCCList.append(
                            {
                                "possMCCList": [],
                                "fullMCSMCC": [
                                    (node,
                                     stage)],
                                "CounterCriteriaA": 1,
                                "durationAandB": 0,
                                "highestMCCnode": "",
                                "frameNum": 0})
                        return potentialMCCList
                    elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
                        potentialMCCList.append(
                            {
                                "possMCCList": [],
                                "fullMCSMCC": [
                                    (node,
                                     stage)],
                                "CounterCriteriaA": 0,
                                "durationAandB": 0,
                                "highestMCCnode": "",
                                "frameNum": 0})
                        return potentialMCCList

            # if predecessor and this frame number already exist in the MCC
            # list, add the current node to the fullMCSMCC list
            if existingFrameFlag:
                if CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                    potentialMCCList[index]["fullMCSMCC"].append((node, stage))
                    potentialMCCList[index]["CounterCriteriaA"] += 1
                    return potentialMCCList
                if not CounterCriteriaAFlag:
                    potentialMCCList[index]["fullMCSMCC"].append((node, stage))
                    return potentialMCCList

        if not predecessorsFlag:
            successorsFlag, index = isThereALink(
                prunedGraph, 2, node, potentialMCCList, 2)

            if successorsFlag:
                for eachNode in potentialMCCList[index]["possMCCList"]:
                    if int(
                            (eachNode[0].split('CE')[0]).split('F')[1]) == frameNum:
                        existingFrameFlag = True

                if CounterCriteriaAFlag and CounterCriteriaBFlag:
                    stage = 'M'
                    potentialMCCList[index]["possMCCList"].append(
                        (node, stage))
                    potentialMCCList[index]["fullMCSMCC"].append((node, stage))

                    if frameNum > potentialMCCList[index]["frameNum"] or potentialMCCList[index]["frameNum"] == 0:
                        potentialMCCList[index]["frameNum"] = frameNum
                        potentialMCCList[index]["highestMCCnode"] = node
                    return potentialMCCList

                if not existingFrameFlag:
                    if stage == 'M':
                        stage = 'D'
                    if CounterCriteriaAFlag and CounterCriteriaBFlag:
                        potentialMCCList[index]["CounterCriteriaA"] += 1
                        potentialMCCList[index]["durationAandB"] += 1
                    elif CounterCriteriaAFlag:
                        potentialMCCList[index]["CounterCriteriaA"] += 1
                    elif CounterCriteriaAFlag == False:
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, stage))
                        return potentialMCCList
                        # if predecessor and this frame number already exist in
                        # the MCC list, add the current node to the fullMCSMCC
                        # list
                else:
                    if CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, stage))
                        potentialMCCList[index]["CounterCriteriaA"] += 1
                        return potentialMCCList
                    if not CounterCriteriaAFlag:
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, stage))
                        return potentialMCCList

        # if this node isn't connected to exisiting MCCs check if it is
        # connected to exisiting MCSs ...
        if predecessorsFlag == False and successorsFlag == False:
            stage = 'I'
            predecessorsMCSFlag, index = isThereALink(
                prunedGraph, 1, node, potentialMCCList, 2)
            if predecessorsMCSFlag:
                if CounterCriteriaAFlag and CounterCriteriaBFlag:
                    potentialMCCList[index]["possMCCList"].append((node, 'M'))
                    potentialMCCList[index]["fullMCSMCC"].append((node, 'M'))
                    potentialMCCList[index]["durationAandB"] += 1
                    if frameNum > potentialMCCList[index]["frameNum"]:
                        potentialMCCList[index]["frameNum"] = frameNum
                        potentialMCCList[index]["highestMCCnode"] = node
                    return potentialMCCList

                if potentialMCCList[index]["frameNum"] == 0 or frameNum <= potentialMCCList[index]["frameNum"]:
                    if CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, stage))
                        potentialMCCList[index]["CounterCriteriaA"] += 1
                        return potentialMCCList
                    elif CounterCriteriaAFlag == False:
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, stage))
                        return potentialMCCList
            else:
                successorsMCSFlag, index = isThereALink(
                    prunedGraph, 2, node, potentialMCCList, 2)
                if successorsMCSFlag:
                    if CounterCriteriaAFlag and CounterCriteriaBFlag:
                        potentialMCCList[index]["possMCCList"].append(
                            (node, 'M'))
                        potentialMCCList[index]["fullMCSMCC"].append(
                            (node, 'M'))

                        potentialMCCList[index]["durationAandB"] += 1
                        if frameNum > potentialMCCList[index]["frameNum"]:
                            potentialMCCList[index]["frameNum"] = frameNum
                            potentialMCCList[index]["highestMCCnode"] = node
                        return potentialMCCList

                    if potentialMCCList[index]["frameNum"] == 0 or frameNum <= potentialMCCList[index]["frameNum"]:
                        if CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                            potentialMCCList[index]["fullMCSMCC"].append(
                                (node, stage))
                            potentialMCCList[index]["CounterCriteriaA"] += 1
                            return potentialMCCList
                        elif CounterCriteriaAFlag == False:
                            potentialMCCList[index]["fullMCSMCC"].append(
                                (node, stage))
                            return potentialMCCList

            # if this node isn't connected to existing MCCs or MCSs, create a
            # new one ...
            if predecessorsFlag == False and predecessorsMCSFlag == False and successorsFlag == False and successorsMCSFlag == False:
                if CounterCriteriaAFlag and CounterCriteriaBFlag:
                    potentialMCCList.append(
                        {
                            "possMCCList": [
                                (node,
                                 stage)],
                            "fullMCSMCC": [
                                (node,
                                 stage)],
                            "CounterCriteriaA": 1,
                            "durationAandB": 1,
                            "highestMCCnode": node,
                            "frameNum": frameNum})
                elif CounterCriteriaAFlag and CounterCriteriaBFlag == False:
                    potentialMCCList.append(
                        {
                            "possMCCList": [],
                            "fullMCSMCC": [
                                (node,
                                 stage)],
                            "CounterCriteriaA": 1,
                            "durationAandB": 0,
                            "highestMCCnode": "",
                            "frameNum": 0})
                elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
                    potentialMCCList.append(
                        {
                            "possMCCList": [],
                            "fullMCSMCC": [
                                (node,
                                 stage)],
                            "CounterCriteriaA": 0,
                            "durationAandB": 0,
                            "highestMCCnode": "",
                            "frameNum": 0})

    return potentialMCCList
#******************************************************************


def isThereALink(prunedGraph, upOrDown, node, potentialMCCList, whichList):
    '''
    Purpose::
            Utility script for updateMCCList mostly because there is no Pythonic way to break out of nested loops

    Input::
            prunedGraph:a Networkx Graph representing all the cloud clusters
            upOrDown: an integer representing 1- to do predecesor check and 2 - to do successor checkedNodesMCC
            node: a string representing the cloud element currently being assessed
            potentialMCCList: a list of dictionaries representing the possible MCCs within a path
            whichList: an integer representing which list ot check in the dictionary; 1- possMCCList, 2- fullMCSMCC

    Output::
            thisFlag: a boolean representing whether the list passed has in the parent or child of the node
            index: an integer representing the location in the potentialMCCList where thisFlag occurs

    '''
    thisFlag = False
    index = -1
    checkList = ""
    if whichList == 1:
        checkList = "possMCCList"
    elif whichList == 2:
        checkList = "fullMCSMCC"

    # check parents
    if upOrDown == 1:
        for aNode in prunedGraph.predecessors(node):
            # reset the index counter for this node search through
            # potentialMCCList
            index = -1
            for MCCDict in potentialMCCList:
                index += 1
                if aNode in list(x[0] for x in MCCDict[checkList]):
                    thisFlag = True
                    # get out of looping so as to avoid the flag being written
                    # over when another node in the predecesor list is checked
                    return thisFlag, index

    # check children
    if upOrDown == 2:
        for aNode in prunedGraph.successors(node):
            # reset the index counter for this node search through
            # potentialMCCList
            index = -1
            for MCCDict in potentialMCCList:
                index += 1

                if aNode in list(x[0] for x in MCCDict[checkList]):
                    thisFlag = True
                    return thisFlag, index

    return thisFlag, index
#******************************************************************


def maxExtentAndEccentricity(eachList):
    '''
    Purpose::
            Perform the final check for MCC based on maximum extent and eccentricity criteria

    Input::
            eachList: a list of strings  representing the node of the possible MCCs within a path

    Output::
            maxShieldNode: a string representing the node with the maximum maxShieldNode
            definiteMCCFlag: a boolean indicating that the MCC has met all requirements

    '''
    maxShieldNode = ''
    maxShieldArea = 0.0
    maxShieldEccentricity = 0.0
    definiteMCCFlag = False

    if eachList:
        for eachNode in eachList:
            if (thisDict(eachNode)['nodeMCSIdentifier'] == 'M' or thisDict(eachNode)[
                    'nodeMCSIdentifier'] == 'D') and thisDict(eachNode)['cloudElementArea'] > maxShieldArea:
                maxShieldNode = eachNode
                maxShieldArea = thisDict(eachNode)['cloudElementArea']

        maxShieldEccentricity = thisDict(maxShieldNode)[
            'cloudElementEccentricity']
        if thisDict(maxShieldNode)['cloudElementEccentricity'] >= ECCENTRICITY_THRESHOLD_MIN and thisDict(
                maxShieldNode)['cloudElementEccentricity'] <= ECCENTRICITY_THRESHOLD_MAX:
            # criteria met
            definiteMCCFlag = True

    return maxShieldNode, definiteMCCFlag
#******************************************************************


def findMaxDepthAndMinPath(thisPathDistanceAndLength):
    '''
    Purpose::
            To determine the maximum depth and min path for the headnode

    Input::
            tuple of dictionaries representing the shortest distance and paths for a node in the tree as returned by nx.single_source_dijkstra
            thisPathDistanceAndLength({distance}, {path})
                    {distance} = nodeAsString, valueAsInt, {path} = nodeAsString, pathAsList

    Output::
            tuple of the max pathLength and min pathDistance as a tuple (like what was input)
                    minDistanceAndMaxPath = ({distance},{path})
    '''
    maxPathLength = 0
    minPath = 0

    # maxPathLength for the node in question
    maxPathLength = max(
        len(values) for values in list(
            thisPathDistanceAndLength[1].values()))

    # if the duration is shorter then the min MCS length, then don't store!
    if maxPathLength < MIN_MCS_DURATION:  # MINIMUM_DURATION :
        minDistanceAndMaxPath = ()

    # else find the min path and max depth
    else:
        # max path distance for the node in question
        minPath = max(
            values for values in list(
                thisPathDistanceAndLength[0].values()))

        # check to determine the shortest path from the longest paths returned
        for pathDistance, path in zip(
            list(
                thisPathDistanceAndLength[0].values()), list(
                thisPathDistanceAndLength[1].values())):
            pathLength = len(path)
            # if pathLength is the same as the maxPathLength, then look the
            # pathDistance to determine if the min
            if pathLength == maxPathLength:
                if pathDistance <= minPath:
                    minPath = pathLength
                    # store details if absolute minPath and deepest
                    minDistanceAndMaxPath = (pathDistance, path)
    return minDistanceAndMaxPath
#******************************************************************


def thisDict(thisNode):
    '''
    Purpose::
            Return dictionary from graph if node exist in tree

    Input::
            thisNode: a string representing the CE to get the information for

    Output ::
            eachdict[1]: a dictionary representing the info associated with thisNode from the graph

    '''
    for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
        if eachdict[1]['uniqueID'] == thisNode:
            return eachdict[1]
#******************************************************************


def checkCriteria(thisCloudElementLatLon, aTemperature):
    '''
    Purpose::
            Determine if criteria B is met for a CEGraph

    Input::
            thisCloudElementLatLon: 2D array of (lat,lon) variable from the node dictionary being currently considered
            aTemperature:a integer representing the temperature maximum for masking

    Output ::
            cloudElementArea: a floating-point number representing the area in the array that meet the criteria - criteriaB

    '''
    cloudElementCriteriaBLatLon = []

    frame, CEcounter = ndimage.measurements.label(
        thisCloudElementLatLon, structure=STRUCTURING_ELEMENT)
    frameCEcounter = 0
    # determine min and max values in lat and lon, then use this to generate
    # teh array from LAT,LON meshgrid

    minLat = min(x[0] for x in thisCloudElementLatLon)
    maxLat = max(x[0]for x in thisCloudElementLatLon)
    minLon = min(x[1]for x in thisCloudElementLatLon)
    maxLon = max(x[1]for x in thisCloudElementLatLon)

    minLatIndex = np.argmax(LAT[:, 0] == minLat)
    maxLatIndex = np.argmax(LAT[:, 0] == maxLat)
    minLonIndex = np.argmax(LON[0, :] == minLon)
    maxLonIndex = np.argmax(LON[0, :] == maxLon)

    criteriaBframe = ma.zeros(
        ((abs(maxLatIndex - minLatIndex) + 1), (abs(maxLonIndex - minLonIndex) + 1)))

    for x in thisCloudElementLatLon:
        # to store the values of the subset in the new array, remove the minLatIndex and minLonindex from the
        # index given in the original array to get the indices for the new
        # array
        criteriaBframe[(np.argmax(LAT[:, 0] == x[0]) - minLatIndex),
                       (np.argmax(LON[0, :] == x[1]) - minLonIndex)] = x[2]

    # keep only those values < aTemperature
    tempMask = ma.masked_array(criteriaBframe, mask=(
        criteriaBframe >= aTemperature), fill_value=0)

    # get the actual values that the mask returned
    criteriaB = ma.zeros((criteriaBframe.shape)).astype('int16')

    for index, value in maenumerate(tempMask):
        lat_index, lon_index = index
        criteriaB[lat_index, lon_index] = value

    for count in range(CEcounter):
        #[0] is time dimension. Determine the actual values from the data
        # loc is a masked array
        #***** returns elements down then across thus (6,4) is 6 arrays deep of size 4
        try:

            loc = ndimage.find_objects(criteriaB)[0]
        except BaseException:            # this would mean that no objects were found meeting criteria B
            print("no objects at this temperature!")
            cloudElementArea = 0.0
            return cloudElementArea, cloudElementCriteriaBLatLon

        try:
            cloudElementCriteriaB = ma.zeros((criteriaB.shape))
            cloudElementCriteriaB = criteriaB[loc]
        except BaseException:
            print("YIKESS")
            print("CEcounter %s %s" % (CEcounter, criteriaB.shape))
            print("criteriaB %s" % criteriaB)

        for index, value in np.ndenumerate(cloudElementCriteriaB):
            if value != 0:
                t, lat, lon = index
                # add back on the minLatIndex and minLonIndex to find the true
                # lat, lon values
                lat_lon_tuple = (LAT[(lat), 0], LON[0, (lon)], value)
                cloudElementCriteriaBLatLon.append(lat_lon_tuple)

        cloudElementArea = np.count_nonzero(
            cloudElementCriteriaB) * XRES * YRES
        # do some cleaning up
        tempMask = []
        criteriaB = []
        cloudElementCriteriaB = []

        return cloudElementArea, cloudElementCriteriaBLatLon
#******************************************************************


def hasMergesOrSplits(nodeList):
    '''
    Purpose::
            Determine if nodes within a path defined from shortest_path splittingNodeDict
    Input::
            nodeList: list of strings representing the nodes from a path
    Output::
            splitList: a list of strings representing all the nodes in the path that split
            mergeList: a list of strings representing all the nodes in the path that merged
    '''
    mergeList = []
    splitList = []

    for node, numParents in list(PRUNED_GRAPH.in_degree(nodeList).items()):
        if numParents > 1:
            mergeList.append(node)

    for node, numChildren in list(PRUNED_GRAPH.out_degree(nodeList).items()):
        if numChildren > 1:
            splitList.append(node)
    # sort
    splitList.sort(key=lambda item: (
        len(item.split('C')[0]), item.split('C')[0]))
    mergeList.sort(key=lambda item: (
        len(item.split('C')[0]), item.split('C')[0]))

    return mergeList, splitList
#******************************************************************


def allAncestors(path, aNode):
    '''
    Purpose::
            Utility script to provide the path leading up to a nodeList

    Input::
            path: a list of strings representing the nodes in the path
            aNode: a string representing a node to be checked for parents

    Output::
            path: a list of strings representing the list of the nodes connected to aNode through its parents
            numOfChildren: an integer representing the number of parents of the node passed
    '''

    numOfParents = PRUNED_GRAPH.in_degree(aNode)
    try:
        if PRUNED_GRAPH.predecessors(aNode) and numOfParents <= 1:
            path = path + PRUNED_GRAPH.predecessors(aNode)
            thisNode = PRUNED_GRAPH.predecessors(aNode)[0]
            return allAncestors(path, thisNode)
        else:
            path = path + aNode
            return path, numOfParents
    except BaseException:
        return path, numOfParents
#******************************************************************


def allDescendants(path, aNode):
    '''
    Purpose::
            Utility script to provide the path leading up to a nodeList

    Input::
            path: a list of strings representing the nodes in the path
            aNode: a string representing a node to be checked for children

    Output::
            path: a list of strings representing the list of the nodes connected to aNode through its children
            numOfChildren: an integer representing the number of children of the node passed
    '''

    numOfChildren = PRUNED_GRAPH.out_degree(aNode)
    try:
        if PRUNED_GRAPH.successors(aNode) and numOfChildren <= 1:
            path = path + PRUNED_GRAPH.successors(aNode)
            thisNode = PRUNED_GRAPH.successors(aNode)[0]
            return allDescendants(path, thisNode)
        else:
            path = path + aNode
            #i.e. PRUNED_GRAPH.predecessors(aNode) is empty
            return path, numOfChildren
    # i.e. PRUNED_GRAPH.predecessors(aNode) threw an exception
    except BaseException:
        return path, numOfChildren
#******************************************************************


def addInfothisDict(thisNode, cloudElementArea, criteriaB):
    '''
    Purpose::
            Update original dictionary node with information

    Input::
            thisNode: a string representing the unique ID of a node
            cloudElementArea: a floating-point number representing the area of the cloud element
            criteriaB: a masked array of floating-point numbers representing the lat,lons meeting the criteria

    Output:: None
    '''
    for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
        if eachdict[1]['uniqueID'] == thisNode:
            eachdict[1]['CriteriaBArea'] = cloudElementArea
            eachdict[1]['CriteriaBLatLon'] = criteriaB
    return
#******************************************************************


def addNodeBehaviorIdentifier(thisNode, nodeBehaviorIdentifier):
    '''
    Purpose:: add an identifier to the node dictionary to indicate splitting, merging or neither node

    Input::
            thisNode: a string representing the unique ID of a node
            nodeBehaviorIdentifier: a string representing the behavior S- split, M- merge, B- both split and merge, N- neither split or merge

    Output :: None

    '''
    for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
        if eachdict[1]['uniqueID'] == thisNode:
            if 'nodeBehaviorIdentifier' not in list(eachdict[1].keys()):
                eachdict[1]['nodeBehaviorIdentifier'] = nodeBehaviorIdentifier
    return
#******************************************************************


def addNodeMCSIdentifier(thisNode, nodeMCSIdentifier):
    '''
    Purpose::
            Add an identifier to the node dictionary to indicate splitting, merging or neither node

    Input::
            thisNode: a string representing the unique ID of a node
            nodeMCSIdentifier: a string representing the stage of the MCS lifecyle  'I' for Initiation, 'M' for Maturity, 'D' for Decay

    Output :: None

    '''
    for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
        if eachdict[1]['uniqueID'] == thisNode:
            if 'nodeMCSIdentifier' not in list(eachdict[1].keys()):
                eachdict[1]['nodeMCSIdentifier'] = nodeMCSIdentifier
    return
#******************************************************************


def updateNodeMCSIdentifier(thisNode, nodeMCSIdentifier):
    '''
    Purpose::
            Update an identifier to the node dictionary to indicate splitting, merging or neither node

    Input::
            thisNode: thisNode: a string representing the unique ID of a node
            nodeMCSIdentifier: a string representing the stage of the MCS lifecyle  'I' for Initiation, 'M' for Maturity, 'D' for Decay

    Output :: None

    '''
    for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
        if eachdict[1]['uniqueID'] == thisNode:
            eachdict[1]['nodeMCSIdentifier'] = nodeBehaviorIdentifier

    return
#******************************************************************


def eccentricity(cloudElementLatLon):
    '''
    Purpose::
            Determines the eccentricity (shape) of contiguous boxes
            Values tending to 1 are more circular by definition, whereas
            values tending to 0 are more linear

    Input::
            cloudElementLatLon: 2D array in (lat,lon) representing T_bb contiguous squares

    Output::
            epsilon: a floating-point representing the eccentricity of the matrix passed

    '''

    epsilon = 0.0

    # loop over all lons and determine longest (non-zero) col
    # loop over all lats and determine longest (non-zero) row
    for latLon in cloudElementLatLon:
        # assign a matrix to determine the legit values

        nonEmptyLons = sum(sum(cloudElementLatLon) > 0)
        nonEmptyLats = sum(sum(cloudElementLatLon.transpose()) > 0)

        lonEigenvalues = 1.0 * nonEmptyLats / \
            (nonEmptyLons + 0.001)  # for long oval on y axis
        latEigenvalues = 1.0 * nonEmptyLons / \
            (nonEmptyLats + 0.001)  # for long oval on x-axs
        epsilon = min(latEigenvalues, lonEigenvalues)

    return epsilon
#******************************************************************


def cloudElementOverlap(currentCELatLons, previousCELatLons):
    '''
    Purpose::
            Determines the percentage overlap between two list of lat-lons passed

    Input::
            currentCELatLons: a list of tuples for the current CE
            previousCELatLons: a list of tuples for the other CE being considered

    Output::
            percentageOverlap: a floating-point representing the number of overlapping lat_lon tuples
            areaOverlap: a floating-point number representing the area overlapping

    '''

    latlonprev = []
    latloncurr = []
    count = 0
    percentageOverlap = 0.0
    areaOverlap = 0.0

    # remove the temperature from the tuples for currentCELatLons and
    # previousCELatLons then check for overlap
    latlonprev = [(x[0], x[1]) for x in previousCELatLons]
    latloncurr = [(x[0], x[1]) for x in currentCELatLons]

    # find overlap
    count = len(list(set(latloncurr) & set(latlonprev)))

    # find area overlap
    areaOverlap = count * XRES * YRES

    # find percentage
    percentageOverlap = max(((count * 1.0) / (len(latloncurr) * 1.0)),
                            ((count * 1.0) / (len(latlonprev) * 1.0)))

    return percentageOverlap, areaOverlap
#******************************************************************


def findCESpeed(node, MCSList):
    '''
    Purpose::
            To determine the speed of the CEs uses vector displacement delta_lat/delta_lon (y/x)

    Input::
            node: a string representing the CE
            MCSList: a list of strings representing the feature

    Output::
            CEspeed: a floating-point number representing the speed of the CE

    '''

    delta_lon = 0.0
    delta_lat = 0.0
    CEspeed = []
    theSpeed = 0.0

    theList = CLOUD_ELEMENT_GRAPH.successors(node)
    nodeLatLon = thisDict(node)['cloudElementCenter']

    for aNode in theList:
        if aNode in MCSList:
            # if aNode is part of the MCSList then determine distance
            aNodeLatLon = thisDict(aNode)['cloudElementCenter']
            # calculate CE speed
            # checking the lats
            # nodeLatLon[0] += 90.0
            # aNodeLatLon[0] += 90.0
            # delta_lat = (nodeLatLon[0] - aNodeLatLon[0])
            delta_lat = (
                (thisDict(node)['cloudElementCenter'][0] + 90.0) - (
                    thisDict(aNode)['cloudElementCenter'][0] + 90.0))
            # nodeLatLon[1] += 360.0
            # aNodeLatLon[1] += 360.0
            # delta_lon = (nodeLatLon[1] - aNodeLatLon[1])
            delta_lon = (
                (thisDict(node)['cloudElementCenter'][1] + 360.0) - (
                    thisDict(aNode)['cloudElementCenter'][1] + 360.0))

            try:
                # convert to s --> m/s
                theSpeed = abs(
                    (((delta_lat / delta_lon) * LAT_DISTANCE * 1000) / (TRES * 3600)))
            except BaseException:
                theSpeed = 0.0

            CEspeed.append(theSpeed)

            # print "~~~ ", thisDict(aNode)['uniqueID']
            # print "*** ", nodeLatLon, thisDict(node)['cloudElementCenter']
            # print "*** ", aNodeLatLon, thisDict(aNode)['cloudElementCenter']

    if not CEspeed:
        return 0.0
    else:
        return min(CEspeed)
#******************************************************************
#
#			UTILITY SCRIPTS FOR MCCSEARCH.PY
#
#******************************************************************


def maenumerate(mArray):
    '''
    Purpose::
            Utility script for returning the actual values from the masked array
            Taken from: http://stackoverflow.com/questions/8620798/numpy-ndenumerate-for-masked-arrays

    Input::
            mArray: the masked array returned from the ma.array() command


    Output::
            maskedValues: 3D (t,lat,lon), value of only masked values

    '''

    mask = ~mArray.mask.ravel()
    # beware yield fast, but generates a type called "generate" that does not
    # allow for array methods
    for index, maskedValue in zip(np.ndenumerate(mArray), mask):
        if maskedValue:
            yield index
#******************************************************************


def createMainDirectory(mainDirStr):
    '''
    Purpose::
            To create the main directory for storing information and
            the subdirectories for storing information
    Input::
            mainDir: a directory for where all information generated from
                    the program are to be stored
    Output:: None

    '''
    global MAINDIRECTORY

    MAINDIRECTORY = mainDirStr
    # if directory doesnt exist, creat it
    if not os.path.exists(MAINDIRECTORY):
        os.makedirs(MAINDIRECTORY)

    os.chdir((MAINDIRECTORY))
    # create the subdirectories
    try:
        os.makedirs('images')
        os.makedirs('textFiles')
        os.makedirs('MERGnetcdfCEs')
        os.makedirs('TRMMnetcdfCEs')
    except BaseException:
        print("Directory exists already!!!")
        # TODO: some nice way of prompting if it is ok to continue...or just
        # leave

    return
#******************************************************************


def checkForFiles(startTime, endTime, thisDir, fileType):
    '''
    Purpose:: To ensure all the files between the starttime and endTime
                      exist in the directory supplied

    Input::
                    startTime: a string yyyymmmddhh representing the starttime
                    endTime: a string yyyymmmddhh representing the endTime
                    thisDir: a string representing the directory path where to
                            look for the file
                    fileType: an integer representing the type of file in the directory
                            1 - MERG original files, 2 - TRMM original files

    Output::
                    status: a boolean representing whether all files exists

    '''
    filelist = []
    startFilename = ''
    endFilename = ''
    currFilename = ''
    status = False
    startyr = int(startTime[:4])
    startmm = int(startTime[4:6])
    startdd = int(startTime[6:8])
    starthr = int(startTime[-2:])
    endyr = int(endTime[:4])
    endmm = int(endTime[4:6])
    enddd = int(endTime[6:8])
    endhh = int(endTime[-2:])
    curryr = startyr
    currmm = startmm
    currdd = startdd
    currhr = starthr
    currmmStr = ''
    currddStr = ''
    currhrStr = ''
    endmmStr = ''
    endddStr = ''
    endhhStr = ''

    # check that the startTime is before the endTime
    if fileType == 1:
        # print "fileType is 1"
        startFilename = "merg_" + startTime + "_4km-pixel.nc"
        endFilename = thisDir + "/merg_" + endTime + "_4km-pixel.nc"

    if fileType == 2:
        # TODO:: determine closest time for TRMM files for end
        # http://disc.sci.gsfc.nasa.gov/additional/faq/precipitation_faq.shtml#convert
        # How do I extract time information from the TRMM 3B42 file name? section
        # startFilename = "3B42."+startTime[:8]+"."+currhr+".7A.nc"
        # endFilename = "3B42."+endTime[:8]+"."+endTime[-2:]+".7A.nc"
        if starthr % 3 == 2:
            currhr += 1
        elif starthr % 3 == 1:
            currhr -= 1
        else:
            currhr = starthr

        curryr, currmmStr, currddStr, currhrStr, _, _, _ = findTime(
            curryr, currmm, currdd, currhr)

        startFilename = "3B42." + \
            str(curryr) + currmmStr + currddStr + "." + currhrStr + ".7A.nc"
        if endhh % 3 == 2:
            endhh += 1
        elif endhh % 3 == 1:
            endhh -= 1

        endyr, endmmStr, endddStr, endhhStr, _, _, _ = findTime(
            endyr, endmm, enddd, endhh)

        endFilename = thisDir + "/3B42." + \
            str(endyr) + endmmStr + endddStr + "." + endhhStr + ".7A.nc"

    # check for files between startTime and endTime
    currFilename = thisDir + "/" + startFilename

    while currFilename is not endFilename:

        if not os.path.isfile(currFilename):
            print("file is missing! Filename: ", currFilename)
            status = False
            return status, filelist
        else:
            # create filelist
            filelist.append(currFilename)

        status = True
        if currFilename == endFilename:
            break

        # generate new currFilename
        if fileType == 1:
            currhr += 1
        elif fileType == 2:
            currhr += 3

        curryr, currmmStr, currddStr, currhrStr, currmm, currdd, currhr = findTime(
            curryr, currmm, currdd, currhr)

        if fileType == 1:
            currFilename = thisDir + "/" + "merg_" + \
                str(curryr) + currmmStr + currddStr + currhrStr + "_4km-pixel.nc"
        if fileType == 2:
            currFilename = thisDir + "/" + "3B42." + \
                str(curryr) + currmmStr + currddStr + "." + currhrStr + ".7A.nc"

    return status, filelist
#******************************************************************


def findTime(curryr, currmm, currdd, currhr):
    '''
    Purpose:: To determine the new yr, mm, dd, hr

    Input:: curryr, an integer representing the year
                    currmm, an integer representing the month
                    currdd, an integer representing the day
                    currhr, an integer representing the hour

    Output::curryr, an integer representing the year
                    currmm, an integer representing the month
                    currdd, an integer representing the day
                    currhr, an integer representing the hour
    '''
    if currhr > 23:
        currhr = 0
        currdd += 1
        if currdd > 30 and (currmm == 4 or currmm ==
                            6 or currmm == 9 or currmm == 11):
            currmm += 1
        elif currdd > 31 and (currmm == 1 or currmm == 3 or currmm == 5 or currmm == 7 or currmm == 8 or currmm == 10):
            currmm += 1
            currdd = 1
        elif currdd > 31 and currmm == 12:
            currmm = 1
            currdd = 1
            curryr += 1
        elif currdd > 28 and currmm == 2 and (curryr % 4) != 0:
            currmm = 3
            currdd = 1
        elif (curryr % 4) == 0 and currmm == 2 and currdd > 29:
            currmm = 3
            currdd = 1

    if currmm < 10:
        currmmStr = "0" + str(currmm)
    else:
        currmmStr = str(currmm)

    if currdd < 10:
        currddStr = "0" + str(currdd)
    else:
        currddStr = str(currdd)

    if currhr < 10:
        currhrStr = "0" + str(currhr)
    else:
        currhrStr = str(currhr)

    return curryr, currmmStr, currddStr, currhrStr, currmm, currdd, currhr
#******************************************************************


def find_nearest(thisArray, value):
    '''
    Purpose :: to determine the value within an array closes to
                    another value

    Input ::
    Output::
    '''
    idx = (np.abs(thisArray - value)).argmin()
    return thisArray[idx]
#******************************************************************

#******************************************************************


def postProcessingNetCDF(dataset, dirName=None):
    '''
    Purpose::
            Utility script displaying the data in NETCDF4 files

    Input::
            dataset: integer representing original MERG (1) or post-processed MERG data (2) or post-processed TRMM(3)
            string: Directory to the location of the raw (MERG) files, preferably zipped

    Output::
       Generates 2D plots in location as specfied in the code

    '''
    coreDir = os.path.dirname(os.path.abspath(__file__))
    imgFilename = ''

    if dataset == 1:
        var = 'ch4'
        plotTitle = 'Original MERG data '
    elif dataset == 2:
        var = 'brightnesstemp'
        plotTitle = 'MERG CE data'
    elif dataset == 3:
        var = 'precipitation_Accumulation'
        plotTitle = 'TRMM CE data'

    # sort files
    os.chdir((dirName + '/'))
    files = list(filter(os.path.isfile, glob.glob("*.nc")))
    files.sort(key=lambda x: os.path.getmtime(x))

    for eachfile in files:
        fullFname = os.path.splitext(eachfile)[0]
        fnameNoExtension = fullFname.split('.nc')[0]

        fname = dirName + '/' + fnameNoExtension + '.nc'

        if os.path.isfile(fname):
            fileData = Dataset(fname, 'r', format='NETCDF4')
            file_variable = fileData.variables[var][:]
            lats = fileData.variables['latitude'][:]
            lons = fileData.variables['longitude'][:]
            LONDATA, LATDATA = np.meshgrid(lons, lats)
            nygrd = len(LATDATA[:, 0])
            nxgrd = len(LONDATA[0, :])
            fileData.close()

        imgFilename = MAINDIRECTORY + '/images/' + fnameNoExtension + '.gif'

        if dataset == 3:
            createPrecipPlot(np.squeeze(file_variable, axis=0),
                             LATDATA[:, 0], LONDATA[0, :], plotTitle, imgFilename)
        else:
            plotter.draw_contour_map(
                file_variable, LATDATA[:, 0], LONDATA[0, :], imgFilename, ptitle=plotTitle)

    return
#******************************************************************


def drawGraph(thisGraph, graphTitle, edgeWeight=None):
    '''
    Purpose::
            Utility function to draw graph in the hierachial format

    Input::
            thisGraph: a Networkx directed graph
            graphTitle: a string representing the graph title
            edgeWeight: (optional) a list of integers representing the edge weights in the graph

    Output:: None

    '''

    imgFilename = MAINDIRECTORY + '/images/' + graphTitle + ".gif"
    fig = plt.figure(facecolor='white', figsize=(16, 12))

    edge95 = [
        (u, v) for (
            u, v, d) in thisGraph.edges(
            data=True) if d['weight'] == edgeWeight[0]]
    edge90 = [
        (u, v) for (
            u, v, d) in thisGraph.edges(
            data=True) if d['weight'] == edgeWeight[1]]
    edegeOverlap = [
        (u, v) for (
            u, v, d) in thisGraph.edges(
            data=True) if d['weight'] == edgeWeight[2]]

    nx.write_dot(thisGraph, 'test.dot')
    plt.title(graphTitle)
    pos = nx.graphviz_layout(thisGraph, prog='dot')
    # draw graph in parts
    # nodes
    nx.draw_networkx_nodes(thisGraph, pos, with_labels=True, arrows=False)
    # edges
    nx.draw_networkx_edges(
        thisGraph,
        pos,
        edgelist=edge95,
        alpha=0.5,
        arrows=False)
    nx.draw_networkx_edges(
        thisGraph,
        pos,
        edgelist=edge90,
        edge_color='b',
        style='dashed',
        arrows=False)
    nx.draw_networkx_edges(
        thisGraph,
        pos,
        edgelist=edegeOverlap,
        edge_color='y',
        style='dashed',
        arrows=False)
    # labels
    nx.draw_networkx_labels(thisGraph, pos, arrows=False)
    plt.axis('off')
    plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
    # do some clean up...and ensuring that we are in the right dir
    os.chdir((MAINDIRECTORY + '/'))
    subprocess.call('rm test.dot', shell=True)
#******************************************************************


def getModelTimes(xtimes, timeVarName):
    '''
    Taken from process.py, removed the file opening at the beginning
    TODO:  Do a better job handling dates here
    Routine to convert from model times ('hours since 1900...', 'days since ...')
    into a python datetime structure

    Input::
        modelFile - path to the model tile you want to extract the times list and modelTimeStep from
        timeVarName - name of the time variable in the model file

    Output::
        times  - list of python datetime objects describing model data times
        modelTimeStep - 'hourly','daily','monthly','annual'
    '''

    from ocw import utils

    timeFormat = xtimes.units
    # search to check if 'since' appears in units
    try:
        sinceLoc = re.search('since', timeFormat).end()

    except AttributeError:
        print("Error decoding model times: time variable attributes do not contain 'since'")
        raise

    units = None
    TIME_UNITS = ('minutes', 'hours', 'days', 'months', 'years')
    # search for 'seconds','minutes','hours', 'days', 'months', 'years' so
    # know units
    for unit in TIME_UNITS:
        if re.search(unit, timeFormat):
            units = unit
            break

    # cut out base time (the bit following 'since')
    base_time_string = string.lstrip(timeFormat[sinceLoc:])
    # decode base time
    base_time = decodeTimeFromString(base_time_string)

    times = []

    for xtime in xtimes[:]:
        # Cast time as an int
        # TODO: KDW this may cause problems for data that is hourly with more
        # than one timestep in it
        xtime = int(xtime)

        if int(xtime) == 0:
            xtime = 1

        if units == 'minutes':
            dt = timedelta(minutes=xtime)
            new_time = base_time + dt
        elif units == 'hours':
            dt = timedelta(hours=int(xtime))
            new_time = base_time + dt  # timedelta(hours=int(xtime))
        elif units == 'days':
            dt = timedelta(days=xtime)
            new_time = base_time + dt
        elif units == 'months':
            # NB. adding months in python is complicated as month length varies and hence ambiguous.
            # Perform date arithmatic manually
            #  Assumption: the base_date will usually be the first of the month
            #              NB. this method will fail if the base time is on the 29th or higher day of month
            #                      -as can't have, e.g. Feb 31st.
            new_month = int(base_time.month + xtime % 12)
            new_year = int(math.floor(base_time.year + xtime / 12.))
            new_time = datetime.datetime(
                new_year,
                new_month,
                base_time.day,
                base_time.hour,
                base_time.second,
                0)
        elif units == 'years':
            dt = datetime.timedelta(years=xtime)
            new_time = base_time + dt

        times.append(new_time)

    try:
        if len(xtimes) == 1:
            timeStepLength = 0
        else:
            timeStepLength = int(xtimes[1] - xtimes[0] + 1.e-12)

        modelTimeStep = getModelTimeStep(units, timeStepLength)

        # if timeStepLength is zero do not normalize times as this would create
        # an empty list for MERG (hourly) data
        if timeStepLength != 0:
            times = normalizeDatetimes(times, modelTimeStep)
    except BaseException:
        raise

    return times, modelTimeStep
#******************************************************************


def getModelTimeStep(units, stepSize):
    # Time units are now determined. Determine the time intervals of input
    # data (mdlTimeStep)
    '''
    Taken from process.py
    '''
    if units == 'minutes':
        if stepSize == 60:
            modelTimeStep = 'hourly'
        elif stepSize == 1440:
            modelTimeStep = 'daily'
        # 28 days through 31 days
        elif 40320 <= stepSize <= 44640:
            modelTimeStep = 'monthly'
        # 365 days through 366 days
        elif 525600 <= stepSize <= 527040:
            modelTimeStep = 'annual'
        else:
            raise Exception(
                'model data time step interval exceeds the max time interval (annual)',
                units,
                stepSize)

    elif units == 'hours':
        # need a check for fractional hrs and only one hr i.e. stepSize=0 e.g.
        # with MERG data
        if stepSize == 0 or stepSize == 1:
            modelTimeStep = 'hourly'
        elif stepSize == 24:
            modelTimeStep = 'daily'
        elif 672 <= stepSize <= 744:
            modelTimeStep = 'monthly'
        elif 8760 <= stepSize <= 8784:
            modelTimeStep = 'annual'
        else:
            raise Exception(
                'model data time step interval exceeds the max time interval (annual)',
                units,
                stepSize)

    elif units == 'days':
        if stepSize == 1:
            modelTimeStep = 'daily'
        elif 28 <= stepSize <= 31:
            modelTimeStep = 'monthly'
        elif 365 <= stepSize <= 366:
            modelTimeStep = 'annual'
        else:
            raise Exception(
                'model data time step interval exceeds the max time interval (annual)',
                units,
                stepSize)

    elif units == 'months':
        if stepSize == 1:
            modelTimeStep = 'monthly'
        elif stepSize == 12:
            modelTimeStep = 'annual'
        else:
            raise Exception(
                'model data time step interval exceeds the max time interval (annual)',
                units,
                stepSize)

    elif units == 'years':
        if stepSize == 1:
            modelTimeStep = 'annual'
        else:
            raise Exception(
                'model data time step interval exceeds the max time interval (annual)',
                units,
                stepSize)

    else:
        errorMessage = 'the time unit ', units, ' is not currently handled in this version.'
        raise Exception(errorMessage)

    return modelTimeStep
#******************************************************************


def decodeTimeFromString(time_string):
    '''
    Taken from process.py
     Decodes string into a python datetime object
     *Method:* tries a bunch of different time format possibilities and hopefully one of them will hit.
     ::

       **Input:**  time_string - a string that represents a date/time

       **Output:** mytime - a python datetime object
    '''
    # This will deal with times that use decimal seconds
    if '.' in time_string:
        time_string = time_string.split('.')[0] + '0'
    else:
        pass

    try:
        mytime = datetime.strptime(time_string, '%Y-%m-%d %H')
        return mytime

    except ValueError:
        pass

    print("Error decoding time string: string does not match a predefined time format'")
    return 0
#******************************************************************


def do_regrid(q, lat, lon, lat2, lon2, order=1, mdi=-999999999):
    """
    This function has been moved to the ocw/dataset_processor module
    """
    from ocw import dataset_processor
    q2 = dataset_processor._rcmes_spatial_regrid(
        q, lat, lon, lat2, lon2, order=1)

    return q2
#******************************************************************
#
#			 METRICS FUNCTIONS FOR MERG.PY
# TODO: rewrite these metrics so that they use the data from the
#	file instead of the graph as this reduce mem resources needed
#
#
#******************************************************************


def numberOfFeatures(finalMCCList):
    '''
    Purpose::
            To count the number of MCCs found for the period

    Input::
            finalMCCList: a list of list of strings representing a list of list of nodes representing a MCC

    Output::
            an integer representing the number of MCCs found

    '''
    return len(finalMCCList)
#******************************************************************


def temporalAndAreaInfoMetric(finalMCCList):
    '''
    Purpose::
            To provide information regarding the temporal properties of the MCCs found

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC

    Output::
            allMCCtimes: a list of dictionaries {MCCtimes, starttime, endtime, duration, area} representing a list of dictionaries
                    of MCC temporal details for each MCC in the period considered

    Assumptions::
            the final time hour --> the event lasted throughout that hr, therefore +1 to endtime
    '''
    # TODO: in real data edit this to use datetime
    #starttime =0
    #endtime =0
    #duration = 0
    MCCtimes = []
    allMCCtimes = []
    MCSArea = []

    if finalMCCList:
        for eachMCC in finalMCCList:
            # get the info from the node
            for eachNode in eachMCC:
                MCCtimes.append(thisDict(eachNode)['cloudElementTime'])
                MCSArea.append(thisDict(eachNode)['cloudElementArea'])

            # sort and remove duplicates
            MCCtimes = sorted(set(MCCtimes))
            tdelta = MCCtimes[1] - MCCtimes[0]
            starttime = MCCtimes[0]
            endtime = MCCtimes[-1]
            duration = (endtime - starttime) + tdelta
            print(
                "starttime: %s endtime: %s tdelta: %s duration: %s MCSAreas %s" %
                (starttime, endtime, tdelta, duration, MCSArea))
            allMCCtimes.append({'MCCtimes': MCCtimes,
                                'starttime': starttime,
                                'endtime': endtime,
                                'duration': duration,
                                'MCSArea': MCSArea})
            MCCtimes = []
            MCSArea = []
    else:
        allMCCtimes = []
        tdelta = 0

    return allMCCtimes, tdelta
#******************************************************************


def longestDuration(allMCCtimes):
    '''
    Purpose::
            To determine the longest MCC for the period

    Input::
            allMCCtimes: a list of dictionaries {MCCtimes, starttime, endtime, duration, area} representing a list of dictionaries
                    of MCC temporal details for each MCC in the period considered

    Output::
            an integer - lenMCC: representing the duration of the longest MCC found
               a list of strings - longestMCC: representing the nodes of longest MCC

    Assumptions::

    '''

    # MCCList = []
    # lenMCC = 0
    # longestMCC =[]

    # #remove duplicates
    # MCCList = list(set(finalMCCList))

    # longestMCC = max(MCCList, key = lambda tup:len(tup))
    # lenMCC = len(longestMCC)

    # return lenMCC, longestMCC

    return max([MCC['duration'] for MCC in allMCCtimes])
#******************************************************************


def shortestDuration(allMCCtimes):
    '''
    Purpose:: To determine the shortest MCC for the period

    Input:: list of dictionaries - allMCCtimes {MCCtimes, starttime, endtime, duration): a list of dictionaries
                      of MCC temporal details for each MCC in the period considered

    Output::an integer - lenMCC: representing the duration of the shortest MCC found
                    a list of strings - longestMCC: representing the nodes of shortest MCC

    Assumptions::

    '''
    # lenMCC = 0
    # shortestMCC =[]
    # MCCList =[]

    # #remove duplicates
    # MCCList = list(set(finalMCCList))

    # shortestMCC = min(MCCList, key = lambda tup:len(tup))
    # lenMCC = len(shortestMCC)

    # return lenMCC, shortestMCC
    return min([MCC['duration'] for MCC in allMCCtimes])
#******************************************************************


def averageDuration(allMCCtimes):
    '''
    Purpose:: To determine the average MCC length for the period

    Input:: list of dictionaries - allMCCtimes {MCCtimes, starttime, endtime, duration): a list of dictionaries
                      of MCC temporal details for each MCC in the period considered

    Output::a floating-point representing the average duration of a MCC in the period

    Assumptions::

    '''

    return sum([MCC['duration'] for MCC in allMCCtimes],
               timedelta(seconds=0)) / len(allMCCtimes)
#******************************************************************


def averageTime(allTimes):
    '''
    Purpose::
            To determine the average time in a list of datetimes
            e.g. of use is finding avg starttime,
    Input::
            allTimes: a list of datetimes representing all of a given event e.g. start time

    Output::
            a floating-point number representing the average of the times given

    '''
    avgTime = 0

    for aTime in allTimes:
        avgTime += aTime.second + 60 * aTime.minute + 3600 * aTime.hour

    if len(allTimes) > 1:
        avgTime /= len(allTimes)

    rez = str(avgTime / 3600) + ' ' + str((avgTime %
                                           3600) / 60) + ' ' + str(avgTime % 60)
    return datetime.strptime(rez, "%H %M %S")
#******************************************************************


def averageFeatureSize(finalMCCList):
    '''
    Purpose:: To determine the average MCC size for the period

    Input:: a list of list of strings - finalMCCList: a list of list of nodes representing a MCC

    Output::a floating-point representing the average area of a MCC in the period

    Assumptions::

    '''
    thisMCC = 0.0
    thisMCCAvg = 0.0

    # for each node in the list, get the are information from the dictionary
    # in the graph and calculate the area
    for eachPath in finalMCCList:
        for eachNode in eachPath:
            thisMCC += thisDict(eachNode)['cloudElementArea']

        thisMCCAvg += (thisMCC / len(eachPath))
        thisMCC = 0.0

    # calcuate final average
    return thisMCCAvg / (len(finalMCCList))
#******************************************************************


def commonFeatureSize(finalMCCList):
    '''
    Purpose::
            To determine the common (mode) MCC size for the period

    Input::
            finalMCCList: a list of list of strings representing the list of nodes representing a MCC

    Output::
            a floating-point representing the average area of a MCC in the period

    Assumptions::

    '''
    thisMCC = 0.0
    thisMCCAvg = []

    # for each node in the list, get the area information from the dictionary
    # in the graph and calculate the area
    for eachPath in finalMCCList:
        for eachNode in eachPath:
            thisMCC += eachNode['cloudElementArea']

        thisMCCAvg.append(thisMCC / len(eachPath))
        thisMCC = 0.0

    # calcuate
    hist, bin_edges = np.histogram(thisMCCAvg)
    return hist, bin_edges
#******************************************************************


def precipTotals(finalMCCList):
    '''
    Purpose::
            Precipitation totals associated with a cloud element

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC

    Output::
            precipTotal: a floating-point number representing the total amount of precipitation associated
                    with the feature
    '''
    precipTotal = 0.0
    CEprecip = 0.0
    MCSPrecip = []
    allMCSPrecip = []
    count = 0

    if finalMCCList:
        # print "len finalMCCList is: ", len(finalMCCList)
        for eachMCC in finalMCCList:
            # get the info from the node
            for node in eachMCC:
                eachNode = thisDict(node)
                count += 1
                if count == 1:
                    prevHr = int(
                        str(eachNode['cloudElementTime']).replace(" ", "")[-8:-6])

                currHr = int(
                    str(eachNode['cloudElementTime']).replace(" ", "")[-8:-6])
                if prevHr == currHr:
                    CEprecip += eachNode['cloudElementPrecipTotal']
                else:
                    MCSPrecip.append((prevHr, CEprecip))
                    CEprecip = eachNode['cloudElementPrecipTotal']
                # last value in for loop
                if count == len(eachMCC):
                    MCSPrecip.append((currHr, CEprecip))

                precipTotal += eachNode['cloudElementPrecipTotal']
                prevHr = currHr

            MCSPrecip.append(('0', precipTotal))

            allMCSPrecip.append(MCSPrecip)
            precipTotal = 0.0
            CEprecip = 0.0
            MCSPrecip = []
            count = 0

        print("allMCSPrecip %s" % allMCSPrecip)

    return allMCSPrecip
#******************************************************************


def precipMaxMin(finalMCCList):
    '''
    TODO: this doesnt work the np.min/max function seems to be not working with the nonzero option..possibly a problem upstream with cloudElementLatLonTRMM
    Purpose::
            Precipitation maximum and min rates associated with each CE in MCS
    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC

    Output::
            MCSPrecip: a list indicating max and min rate for each CE identified

    '''
    maxCEprecip = 0.0
    minCEprecip = 0.0
    MCSPrecip = []
    allMCSPrecip = []

    if finalMCCList:
        if isinstance(finalMCCList[0], str):  # len(finalMCCList) == 1:
            for node in finalMCCList:
                eachNode = thisDict(node)
                CETRMM = eachNode['cloudElementLatLonTRMM']

                print("all %s" % np.min(CETRMM[np.nonzero(CETRMM)]))
                print("minCEprecip %s" %
                      np.min(eachNode['cloudElementLatLonTRMM']))

                print("maxCEprecip %s" % np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(
                    eachNode['cloudElementLatLonTRMM'])]))
                sys.exit()
                maxCEprecip = np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(
                    eachNode['cloudElementLatLonTRMM'])])
                minCEprecip = np.min(eachNode['cloudElementLatLonTRMM'][np.nonzero(
                    eachNode['cloudElementLatLonTRMM'])])
                MCSPrecip.append(
                    (eachNode['uniqueID'], minCEprecip, maxCEprecip))

        else:
            for eachMCC in finalMCCList:
                # get the info from the node
                for node in eachMCC:
                    eachNode = thisDict(node)
                    # find min and max precip
                    maxCEprecip = np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(
                        eachNode['cloudElementLatLonTRMM'])])
                    minCEprecip = np.min(eachNode['cloudElementLatLonTRMM'][np.nonzero(
                        eachNode['cloudElementLatLonTRMM'])])
                    MCSPrecip.append(
                        (eachNode['uniqueID'], minCEprecip, maxCEprecip))
                allMCSPrecip.append(MCSPrecip)
                MCSPrecip = []

    return MCSPrecip
#******************************************************************
#
#							PLOTS
#
#******************************************************************


def displaySize(finalMCCList):
    '''
    Purpose::
            To create a figure showing the area verse time for each MCS

    Input::
            finalMCCList: a list of list of strings representing the list of nodes representing a MCC

    Output::
            None

    '''
    timeList = []
    count = 1
    imgFilename = ''
    minArea = 10000.0
    maxArea = 0.0
    eachNode = {}

    # for each node in the list, get the area information from the dictionary
    # in the graph and calculate the area

    if finalMCCList:
        for eachMCC in finalMCCList:
            # get the info from the node
            for node in eachMCC:
                eachNode = thisDict(node)
                timeList.append(eachNode['cloudElementTime'])

                if eachNode['cloudElementArea'] < minArea:
                    minArea = eachNode['cloudElementArea']
                if eachNode['cloudElementArea'] > maxArea:
                    maxArea = eachNode['cloudElementArea']

            # sort and remove duplicates
            timeList = sorted(set(timeList))
            tdelta = timeList[1] - timeList[0]
            starttime = timeList[0] - tdelta
            endtime = timeList[-1] + tdelta
            timeList.insert(0, starttime)
            timeList.append(endtime)

            # plot info
            plt.close('all')
            title = 'Area distribution of the MCC over somewhere'
            # figsize=(10,8))#figsize=(16,12))
            fig = plt.figure(facecolor='white', figsize=(18, 10))
            fig, ax = plt.subplots(1, facecolor='white', figsize=(10, 10))

            # the data
            for node in eachMCC:  # for eachNode in eachMCC:
                eachNode = thisDict(node)
                if eachNode['cloudElementArea'] < 80000:  # 2400.00:
                    ax.plot(
                        eachNode['cloudElementTime'],
                        eachNode['cloudElementArea'],
                        'bo',
                        markersize=10)
                elif eachNode['cloudElementArea'] >= 80000.00 and eachNode['cloudElementArea'] < 160000.00:
                    ax.plot(
                        eachNode['cloudElementTime'],
                        eachNode['cloudElementArea'],
                        'yo',
                        markersize=20)
                else:
                    ax.plot(
                        eachNode['cloudElementTime'],
                        eachNode['cloudElementArea'],
                        'ro',
                        markersize=30)

            #axes and labels
            maxArea += 1000.00
            ax.set_xlim(starttime, endtime)
            ax.set_ylim(minArea, maxArea)
            ax.set_ylabel('Area in km^2', fontsize=12)
            ax.set_title(title)
            ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d%H:%M:%S')
            fig.autofmt_xdate()
            plt.subplots_adjust(bottom=0.2)

            imgFilename = MAINDIRECTORY + '/images/' + str(count) + 'MCS.gif'
            plt.savefig(
                imgFilename,
                facecolor=fig.get_facecolor(),
                transparent=True)

            # if time in not already in the time list, append it
            timeList = []
            count += 1
    return
#******************************************************************


def displayPrecip(finalMCCList):
    '''
    Purpose::
            To create a figure showing the precip rate verse time for each MCS

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC

    Output:: None

    '''
    timeList = []
    oriTimeList = []
    colorBarTime = []
    count = 1
    imgFilename = ''
    TRMMprecipDis = []
    percentagePrecipitating = []  # 0.0
    CEArea = []
    nodes = []
    xy = []
    x = []
    y = []
    precip = []
    partialArea = []
    totalSize = 0.0

    firstTime = True
    xStart = 0.0
    yStart = 0.0

    num_bins = 5

    # for each node in the list, get the area information from the dictionary
    # in the graph and calculate the area

    if finalMCCList:
        for eachMCC in finalMCCList:
            # get the info from the node
            for node in eachMCC:
                eachNode = thisDict(node)
                if firstTime:
                    xStart = eachNode['cloudElementCenter'][1]  # lon
                    yStart = eachNode['cloudElementCenter'][0]  # lat
                timeList.append(eachNode['cloudElementTime'])
                percentagePrecipitating.append(
                    (eachNode['TRMMArea'] / eachNode['cloudElementArea']) * 100.0)
                CEArea.append(eachNode['cloudElementArea'])
                nodes.append(eachNode['uniqueID'])
                # print eachNode['uniqueID'],
                # eachNode['cloudElementCenter'][1],
                # eachNode['cloudElementCenter'][0]
                x.append(eachNode['cloudElementCenter'][1])  # -xStart)
                y.append(eachNode['cloudElementCenter'][0])  # -yStart)

                firstTime = False

            # convert the timeList[] to list of floats
            for i in range(len(timeList)):  # oriTimeList:
                colorBarTime.append(time.mktime(timeList[i].timetuple()))

            totalSize = sum(CEArea)
            partialArea = [(a / totalSize) * 30000 for a in CEArea]

            # print "x ", x
            # print "y ", y

            # plot info
            plt.close('all')

            title = 'Precipitation distribution of the MCS '
            fig, ax = plt.subplots(1, facecolor='white', figsize=(20, 7))

            cmap = plt.jet
            ax.scatter(
                x,
                y,
                s=partialArea,
                c=colorBarTime,
                edgecolors='none',
                marker='o',
                cmap=cmap)
            colorBarTime = []
            colorBarTime = sorted(set(timeList))
            cb = colorbar_index(
                ncolors=len(colorBarTime),
                nlabels=colorBarTime,
                cmap=cmap)

            #axes and labels
            ax.set_xlabel('Degrees Longtude', fontsize=12)
            ax.set_ylabel('Degrees Latitude', fontsize=12)
            ax.set_title(title)
            ax.grid(True)
            plt.subplots_adjust(bottom=0.2)

            for i, txt in enumerate(nodes):
                if CEArea[i] >= 2400.00:
                    ax.annotate('%d' %
                                percentagePrecipitating[i] +
                                '%', (x[i], y[i]))
                precip = []

            imgFilename = MAINDIRECTORY + \
                '/images/MCSprecip' + str(count) + '.gif'
            plt.savefig(
                imgFilename,
                facecolor=fig.get_facecolor(),
                transparent=True)

            # reset for next image
            timeList = []
            percentagePrecipitating = []
            CEArea = []
            x = []
            y = []
            colorBarTime = []
            nodes = []
            precip = []
            count += 1
            firstTime = True
    return
#******************************************************************


def plotPrecipHistograms(finalMCCList, num_bins=5):
    '''
    Purpose::
            To create plots (histograms) of the each TRMMnetcdfCEs files

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC
            num_bins: an integer representing the number of bins
    Output::
            plots
    '''

    precip = []
    imgFilename = " "
    lastTime = " "
    firstTime = True
    MCScount = 0
    MSClen = 0
    thisCount = 0
    totalPrecip = np.zeros((1, 137, 440))

    # TODO: use try except block instead
    if finalMCCList:

        for eachMCC in finalMCCList:
            firstTime = True
            MCScount += 1
            # totalPrecip=np.zeros((1,137,440))
            totalPrecip = np.zeros((1, 413, 412))

            # get the info from the node
            for node in eachMCC:
                eachNode = thisDict(node)
                thisTime = eachNode['cloudElementTime']
                MCSlen = len(eachMCC)
                thisCount += 1

                # this is the precipitation distribution plot from
                # displayPrecip

                if eachNode['cloudElementArea'] >= 2400.0:
                    if (str(thisTime) != lastTime and lastTime !=
                            " ") or thisCount == MCSlen:
                        # plt.close('all')
                        # title = 'TRMM precipitation distribution for '+ str(thisTime)

                        # fig,ax = plt.subplots(1, facecolor='white', figsize=(7,5))

                        # n,binsdg = np.histogram(precip, num_bins)
                        # wid = binsdg[1:] - binsdg[:-1]
                        # plt.bar(binsdg[:-1], n/float(len(precip)), width=wid)

                        # #make percentage plot
                        # formatter = FuncFormatter(to_percent)
                        # plt.xlim(min(binsdg), max(binsdg))
                        # ax.set_xticks(binsdg)
                        # ax.set_xlabel('Precipitation [mm]', fontsize=12)
                        # ax.set_ylabel('Area', fontsize=12)
                        # ax.set_title(title)
                        # # Set the formatter
                        # plt.gca().yaxis.set_major_formatter(formatter)
                        # plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%0.0f'))
                        # imgFilename = MAINDIRECTORY+'/images/'+str(thisTime)+eachNode['uniqueID']+'TRMMMCS.gif'

                        # plt.savefig(imgFilename, transparent=True)
                        data_names = ['Precipitation [mm]', 'Area']
                        plotter.draw_histogram(
                            precip, data_names, imgFilename, num_bins)
                        precip = []

                    # ------ NETCDF File get info -----------------------------
                    thisFileName = MAINDIRECTORY + '/TRMMnetcdfCEs/TRMM' + \
                        str(thisTime).replace(" ", "_") + eachNode['uniqueID'] + '.nc'
                    TRMMData = Dataset(thisFileName, 'r', format='NETCDF4')
                    precipRate = TRMMData.variables['precipitation_Accumulation'][:, :, :]
                    CEprecipRate = precipRate[0, :, :]
                    TRMMData.close()
                    if firstTime:
                        totalPrecip = np.zeros((CEprecipRate.shape))

                    totalPrecip = np.add(totalPrecip, precipRate)
                    # ------ End NETCDF File ----------------------------------
                    for index, value in np.ndenumerate(CEprecipRate):
                        if value != 0.0:
                            precip.append(value)

                    lastTime = str(thisTime)
                    firstTime = False
                else:
                    lastTime = str(thisTime)
                    firstTime = False
    return
#******************************************************************


def plotAccTRMM(finalMCCList):
    '''
    Purpose::
            (1) generate a file with the accumulated precipiation for the MCS
            (2) generate the appropriate image
            TODO: NB: as the domain changes, will need to change XDEF and YDEF by hand to accomodate the new domain
            TODO: look into getting the info from the NETCDF file

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC

    Output::
            a netcdf file containing the accumulated precip
            a 2D matlablibplot
    '''
    os.chdir((MAINDIRECTORY + '/TRMMnetcdfCEs'))
    fname = ''
    imgFilename = ''
    firstPartName = ''
    firstTime = True
    replaceExpXDef = ''

    # generate the file name using MCCTimes
    # if the file name exists, add it to the accTRMM file
    for path in finalMCCList:
        for eachNode in path:
            thisNode = thisDict(eachNode)
            fname = 'TRMM' + \
                str(thisNode['cloudElementTime']).replace(" ", "_") + thisNode['uniqueID'] + '.nc'

            if os.path.isfile(fname):
                # open NetCDF file add info to the accu
                # print "opening TRMM file ", fname
                TRMMCEData = Dataset(fname, 'r', format='NETCDF4')
                precipRate = TRMMCEData.variables['precipitation_Accumulation'][:]
                lats = TRMMCEData.variables['latitude'][:]
                lons = TRMMCEData.variables['longitude'][:]
                LONTRMM, LATTRMM = np.meshgrid(lons, lats)
                nygrdTRMM = len(LATTRMM[:, 0])
                nxgrdTRMM = len(LONTRMM[0, :])
                precipRate = ma.masked_array(
                    precipRate, mask=(precipRate < 0.0))
                TRMMCEData.close()

                if firstTime:
                    firstPartName = str(
                        thisNode['cloudElementTime']).replace(
                        " ", "_") + '-'
                    accuPrecipRate = ma.zeros((precipRate.shape))
                    firstTime = False

                accuPrecipRate += precipRate

        imgFilename = MAINDIRECTORY + '/images/MCSaccu' + firstPartName + \
            str(thisNode['cloudElementTime']).replace(" ", "_") + '.gif'

    # create new netCDF file
    accuTRMMFile = MAINDIRECTORY + '/TRMMnetcdfCEs/accu' + firstPartName + \
        str(thisNode['cloudElementTime']).replace(" ", "_") + '.nc'
    # write the file
    accuTRMMData = Dataset(accuTRMMFile, 'w', format='NETCDF4')
    accuTRMMData.description = 'Accumulated precipitation data'
    accuTRMMData.calendar = 'standard'
    accuTRMMData.conventions = 'COARDS'
    # dimensions
    accuTRMMData.createDimension('time', None)
    accuTRMMData.createDimension('lat', nygrdTRMM)
    accuTRMMData.createDimension('lon', nxgrdTRMM)

    # variables
    TRMMprecip = ('time', 'lat', 'lon',)
    times = accuTRMMData.createVariable('time', 'f8', ('time',))
    times.units = 'hours since ' + \
        str(thisNode['cloudElementTime']).replace(" ", "_")[:-6]
    latitude = accuTRMMData.createVariable('latitude', 'f8', ('lat',))
    longitude = accuTRMMData.createVariable('longitude', 'f8', ('lon',))
    rainFallacc = accuTRMMData.createVariable(
        'precipitation_Accumulation', 'f8', TRMMprecip)
    rainFallacc.units = 'mm'

    longitude[:] = LONTRMM[0, :]
    longitude.units = "degrees_east"
    longitude.long_name = "Longitude"

    latitude[:] = LATTRMM[:, 0]
    latitude.units = "degrees_north"
    latitude.long_name = "Latitude"

    rainFallacc[:] = accuPrecipRate[:]

    accuTRMMData.close()

    # do plot
    plotTitle = 'TRMM Accumulated [mm]'
    createPrecipPlot(np.squeeze(accuPrecipRate, axis=0),
                     LATTRMM[:, 0], LONTRMM[0, :], plotTitle, imgFilename)

    return
#******************************************************************


def plotAccuInTimeRange(starttime, endtime):
    '''
    Purpose::
            Create accumulated precip plot within a time range given using all CEs

    Input::
            starttime: a string representing the time to start the accumulations format yyyy-mm-dd_hh:mm:ss
            endtime: a string representing the time to end the accumulations format yyyy-mm-dd_hh:mm:ss

    Output::
            a netcdf file containing the accumulated precip for specified times
            a 2D matlablibplot

    '''

    os.chdir((MAINDIRECTORY + '/TRMMnetcdfCEs/'))

    imgFilename = ''
    firstPartName = ''
    firstTime = True

    fileList = []
    sTime = datetime.strptime(starttime.replace("_", " "), '%Y-%m-%d %H:%M:%S')
    eTime = datetime.strptime(endtime.replace("_", " "), '%Y-%m-%d %H:%M:%S')
    thisTime = sTime

    while thisTime <= eTime:
        fileList = list(
            filter(
                os.path.isfile,
                glob.glob(
                    ('TRMM' +
                     str(thisTime).replace(
                         " ",
                         "_") +
                        '*' +
                        '.nc'))))
        for fname in fileList:
            TRMMCEData = Dataset(fname, 'r', format='NETCDF4')
            precipRate = TRMMCEData.variables['precipitation_Accumulation'][:]
            lats = TRMMCEData.variables['latitude'][:]
            lons = TRMMCEData.variables['longitude'][:]
            LONTRMM, LATTRMM = np.meshgrid(lons, lats)
            nygrdTRMM = len(LATTRMM[:, 0])
            nxgrdTRMM = len(LONTRMM[0, :])
            precipRate = ma.masked_array(precipRate, mask=(precipRate < 0.0))
            TRMMCEData.close()

            if firstTime:
                accuPrecipRate = ma.zeros((precipRate.shape))
                firstTime = False

            accuPrecipRate += precipRate

        # increment the time
        thisTime += timedelta(hours=TRES)

    # create new netCDF file
    accuTRMMFile = MAINDIRECTORY + '/TRMMnetcdfCEs/accu' + \
        starttime + '-' + endtime + '.nc'
    print("accuTRMMFile %s" % accuTRMMFile)
    # write the file
    accuTRMMData = Dataset(accuTRMMFile, 'w', format='NETCDF4')
    accuTRMMData.description = 'Accumulated precipitation data'
    accuTRMMData.calendar = 'standard'
    accuTRMMData.conventions = 'COARDS'
    # dimensions
    accuTRMMData.createDimension('time', None)
    accuTRMMData.createDimension('lat', nygrdTRMM)
    accuTRMMData.createDimension('lon', nxgrdTRMM)

    # variables
    TRMMprecip = ('time', 'lat', 'lon',)
    times = accuTRMMData.createVariable('time', 'f8', ('time',))
    times.units = 'hours since ' + starttime[:-6]
    latitude = accuTRMMData.createVariable('latitude', 'f8', ('lat',))
    longitude = accuTRMMData.createVariable('longitude', 'f8', ('lon',))
    rainFallacc = accuTRMMData.createVariable(
        'precipitation_Accumulation', 'f8', TRMMprecip)
    rainFallacc.units = 'mm'

    longitude[:] = LONTRMM[0, :]
    longitude.units = "degrees_east"
    longitude.long_name = "Longitude"

    latitude[:] = LATTRMM[:, 0]
    latitude.units = "degrees_north"
    latitude.long_name = "Latitude"
    rainFallacc[:] = accuPrecipRate[:]

    accuTRMMData.close()

    # plot the stuff
    imgFilename = MAINDIRECTORY + '/images/accu' + starttime + '-' + endtime + '.gif'
    plotTitle = "TRMM Accumulated Precipitation [mm] " + \
        starttime + '-' + endtime
    createPrecipPlot(np.squeeze(accuPrecipRate, axis=0),
                     LATTRMM[:, 0], LONTRMM[0, :], plotTitle, imgFilename)

    return
#******************************************************************


def createPrecipPlot(dataset, lats, lons, plotTitle, imgFilename):
    '''
    Purpose::
            To create the actual plots for precip data only

    Input::
            dataset: a 2d numpy (lon,lat) dataset of the precip data to be plotted
            domainDict: a dictionary with the domain (lons and lats) details required
            plotTitle: a string representing the title for the plot
            imgFilename: a string representing the string (including path) of where the plot is to be showed

    Output::
            A 2D plot with precipitation using the NWS precipitation colormap (from matlplotlib Basemap)

    '''

    fig, ax = plt.subplots(
        1, facecolor='white', figsize=(
            8.5, 11.))  # , dpi=300)
    latmin = np.min(lats)
    latmax = np.max(lats)
    lonmin = np.min(lons)
    lonmax = np.max(lons)

    m = Basemap(
        projection='merc',
        llcrnrlon=lonmin,
        urcrnrlon=lonmax,
        llcrnrlat=latmin,
        urcrnrlat=latmax,
        resolution='l',
        ax=ax)
    m.drawcoastlines(linewidth=1)
    m.drawcountries(linewidth=0.75)
    # draw meridians
    meridians = np.arange(180., 360., 5.)
    m.drawmeridians(
        meridians,
        labels=[
            0,
            0,
            0,
            1],
        linewidth=0.75,
        fontsize=10)
    # draw parallels
    parallels = np.arange(0., 90, 5.)
    m.drawparallels(
        parallels,
        labels=[
            1,
            0,
            0,
            0],
        linewidth=0.75,
        fontsize=10)

    # projecting on to the correct map grid
    longitudes, latitudes = m.makegrid(lons.shape[0], lats.shape[0])
    x, y = m(longitudes, latitudes)

    # draw filled contours.
    clevs = [0, 1, 2.5, 5, 7.5, 10, 15, 20, 30, 40, 50,
             70, 100, 150, 200, 250, 300, 400, 500, 600, 750]

    # actually print the map
    cs = m.contourf(x, y, dataset, clevs, cmap=cmbm.s3pcpn)

    # add colorbar
    cbar = m.colorbar(cs, location='bottom', pad="10%")
    cbar.set_label('mm')

    plt.title(plotTitle)

    plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
    return
#******************************************************************


def createTextFile(finalMCCList, identifier):
    '''
    Purpose::
            Create a text file with information about the MCS
            This function is expected to be especially of use regarding long term record checks

    Input::
            finalMCCList: a list of dictionaries representing a list of nodes representing a MCC
            identifier: an integer representing the type of list that has been entered...this is for creating file purposes
                    1 - MCCList; 2- MCSList

    Output::
            a user readable text file with all information about each MCS
            a user readable text file with the summary of the MCS

    Assumptions::
    '''

    durations = 0.0
    startTimes = []
    endTimes = []
    averagePropagationSpeed = 0.0
    speedCounter = 0
    maxArea = 0.0
    amax = 0.0
    avgMaxArea = []
    maxAreaCounter = 0.0
    maxAreaTime = ''
    eccentricity = 0.0
    firstTime = True
    matureFlag = True
    timeMCSMatures = ''
    maxCEprecipRate = 0.0
    minCEprecipRate = 0.0
    averageArea = 0.0
    averageAreaCounter = 0
    durationOfMatureMCC = 0
    avgMaxPrecipRate = 0.0
    avgMaxPrecipRateCounter = 0
    avgMinPrecipRate = 0.0
    avgMinPrecipRateCounter = 0
    CEspeed = 0.0
    MCSspeed = 0.0
    MCSspeedCounter = 0
    MCSPrecipTotal = 0.0
    avgMCSPrecipTotalCounter = 0
    bigPtotal = 0.0
    bigPtotalCounter = 0
    allPropagationSpeeds = []
    averageAreas = []
    areaAvg = 0.0
    avgPrecipTotal = 0.0
    avgPrecipTotalCounter = 0
    avgMaxMCSPrecipRate = 0.0
    avgMaxMCSPrecipRateCounter = 0
    avgMinMCSPrecipRate = 0.0
    avgMinMCSPrecipRateCounter = 0
    minMax = []
    avgPrecipArea = []
    location = []
    avgPrecipAreaPercent = 0.0
    precipArea = 0.0
    precipAreaPercent = 0.0
    precipPercent = []
    precipCounter = 0
    precipAreaAvg = 0.0
    minSpeed = 0.0
    maxSpeed = 0.0

    if identifier == 1:
        MCSUserFile = open(
            (MAINDIRECTORY + '/textFiles/MCCsUserFile.txt'), 'wb')
        MCSSummaryFile = open(
            (MAINDIRECTORY + '/textFiles/MCCSummary.txt'), 'wb')
        MCSPostFile = open(
            (MAINDIRECTORY + '/textFiles/MCCPostPrecessing.txt'), 'wb')

    if identifier == 2:
        MCSUserFile = open(
            (MAINDIRECTORY + '/textFiles/MCSsUserFile.txt'), 'wb')
        MCSSummaryFile = open(
            (MAINDIRECTORY + '/textFiles/MCSSummary.txt'), 'wb')
        MCSPostFile = open(
            (MAINDIRECTORY + '/textFiles/MCSPostPrecessing.txt'), 'wb')

    for eachPath in finalMCCList:
        eachPath.sort(key=lambda nodeID: (
            len(nodeID.split('C')[0]), nodeID.split('C')[0], nodeID.split('CE')[1]))
        MCSPostFile.write("\n %s" % eachPath)

        startTime = thisDict(eachPath[0])['cloudElementTime']
        endTime = thisDict(eachPath[-1])['cloudElementTime']
        duration = (endTime - startTime) + timedelta(hours=TRES)

        # convert datatime duration to seconds and add to the total for the
        # average duration of all MCS in finalMCCList
        durations += (duration.total_seconds())

        #durations += duration
        startTimes.append(startTime)
        endTimes.append(endTime)

        # get the precip info

        for eachNode in eachPath:

            thisNode = thisDict(eachNode)

            # set first time min "fake" values
            if firstTime:
                minCEprecipRate = thisNode['CETRMMmin']
                avgMinMCSPrecipRate += thisNode['CETRMMmin']
                firstTime = False

            # calculate the speed
            if thisNode['cloudElementArea'] >= OUTER_CLOUD_SHIELD_AREA:
                averagePropagationSpeed += findCESpeed(eachNode, eachPath)
                speedCounter += 1

            # Amax: find max area
            if thisNode['cloudElementArea'] > maxArea:
                maxArea = thisNode['cloudElementArea']
                maxAreaTime = str(thisNode['cloudElementTime'])
                eccentricity = thisNode['cloudElementEccentricity']
                location = thisNode['cloudElementCenter']

                # determine the time the feature matures
                if matureFlag:
                    timeMCSMatures = str(thisNode['cloudElementTime'])
                    matureFlag = False

            # find min and max precip rate
            if thisNode['CETRMMmin'] < minCEprecipRate:
                minCEprecipRate = thisNode['CETRMMmin']

            if thisNode['CETRMMmax'] > maxCEprecipRate:
                maxCEprecipRate = thisNode['CETRMMmax']

            # calculations for only the mature stage
            if thisNode['nodeMCSIdentifier'] == 'M':
                # calculate average area of the maturity feature only
                averageArea += thisNode['cloudElementArea']
                averageAreaCounter += 1
                durationOfMatureMCC += 1
                avgMaxPrecipRate += thisNode['CETRMMmax']
                avgMaxPrecipRateCounter += 1
                avgMinPrecipRate += thisNode['CETRMMmin']
                avgMinPrecipRateCounter += 1
                avgMaxMCSPrecipRate += thisNode['CETRMMmax']
                avgMaxMCSPrecipRateCounter += 1
                avgMinMCSPrecipRate += thisNode['CETRMMmin']
                avgMinMCSPrecipRateCounter += 1

                # the precip percentage (TRMM area/CE area)
                if thisNode['cloudElementArea'] >= 0.0 and thisNode['TRMMArea'] >= 0.0:
                    precipArea += thisNode['TRMMArea']
                    avgPrecipArea.append(thisNode['TRMMArea'])
                    avgPrecipAreaPercent += (
                        thisNode['TRMMArea'] / thisNode['cloudElementArea'])
                    precipPercent.append(
                        (thisNode['TRMMArea'] / thisNode['cloudElementArea']))
                    precipCounter += 1

                # system speed for only mature stage
                CEspeed = findCESpeed(eachNode, eachPath)
                if CEspeed > 0.0:
                    MCSspeed += CEspeed
                    MCSspeedCounter += 1

            # find accumulated precip
            if thisNode['cloudElementPrecipTotal'] > 0.0:
                MCSPrecipTotal += thisNode['cloudElementPrecipTotal']
                avgMCSPrecipTotalCounter += 1

        # A: calculate the average Area of the (mature) MCS
        if averageAreaCounter > 0:  # and averageAreaCounter > 0:
            averageArea /= averageAreaCounter
            averageAreas.append(averageArea)

        # v: MCS speed
        if MCSspeedCounter > 0:  # and MCSspeed > 0.0:
            MCSspeed /= MCSspeedCounter

        # smallP_max: calculate the average max precip rate (mm/h)
        if avgMaxMCSPrecipRateCounter > 0:  # and avgMaxPrecipRate > 0.0:
            avgMaxMCSPrecipRate /= avgMaxMCSPrecipRateCounter

        # smallP_min: calculate the average min precip rate (mm/h)
        if avgMinMCSPrecipRateCounter > 0:  # and avgMinPrecipRate > 0.0:
            avgMinMCSPrecipRate /= avgMinMCSPrecipRateCounter

        # smallP_avg: calculate the average precipitation (mm hr-1)
        if MCSPrecipTotal > 0.0:  # and avgMCSPrecipTotalCounter> 0:
            avgMCSPrecipTotal = MCSPrecipTotal / avgMCSPrecipTotalCounter
            avgPrecipTotal += avgMCSPrecipTotal
            avgPrecipTotalCounter += 1

        #smallP_total = MCSPrecipTotal
        # precip over the MCS lifetime prep for bigP_total
        if MCSPrecipTotal > 0.0:
            bigPtotal += MCSPrecipTotal
            bigPtotalCounter += 1

        if maxArea > 0.0:
            avgMaxArea.append(maxArea)
            maxAreaCounter += 1

        # verage precipate area precentage (TRMM/CE area)
        if precipCounter > 0:
            avgPrecipAreaPercent /= precipCounter
            precipArea /= precipCounter

        # write stuff to file
        MCSUserFile.write("\n\n\nStarttime is: %s " % (str(startTime)))
        MCSUserFile.write("\nEndtime is: %s " % (str(endTime)))
        MCSUserFile.write("\nLife duration is %s hrs" % (str(duration)))
        MCSUserFile.write("\nTime of maturity is %s " % (timeMCSMatures))
        MCSUserFile.write(
            "\nDuration mature stage is: %s " %
            durationOfMatureMCC * TRES)
        MCSUserFile.write("\nAverage area is: %.4f km^2 " % (averageArea))
        MCSUserFile.write("\nMax area is: %.4f km^2 " % (maxArea))
        MCSUserFile.write("\nMax area time is: %s " % (maxAreaTime))
        MCSUserFile.write(
            "\nEccentricity at max area is: %.4f " %
            (eccentricity))
        MCSUserFile.write(
            "\nCenter (lat,lon) at max area is: %.2f\t%.2f" %
            (location[0], location[1]))
        MCSUserFile.write("\nPropagation speed is %.4f " % (MCSspeed))
        MCSUserFile.write(
            "\nMCS minimum preicip rate is %.4f mmh^-1" %
            (minCEprecipRate))
        MCSUserFile.write(
            "\nMCS maximum preicip rate is %.4f mmh^-1" %
            (maxCEprecipRate))
        MCSUserFile.write(
            "\nTotal precipitation during MCS is %.4f mm/lifetime" %
            (MCSPrecipTotal))
        MCSUserFile.write(
            "\nAverage MCS precipitation is %.4f mm" %
            (avgMCSPrecipTotal))
        MCSUserFile.write(
            "\nAverage MCS maximum precipitation is %.4f mmh^-1" %
            (avgMaxMCSPrecipRate))
        MCSUserFile.write(
            "\nAverage MCS minimum precipitation is %.4f mmh^-1" %
            (avgMinMCSPrecipRate))
        MCSUserFile.write(
            "\nAverage precipitation area is %.4f km^2 " %
            (precipArea))
        MCSUserFile.write(
            "\nPrecipitation area percentage of mature system %.4f percent " %
            (avgPrecipAreaPercent * 100))

        # append stuff to lists for the summary file
        if MCSspeed > 0.0:
            allPropagationSpeeds.append(MCSspeed)
            averagePropagationSpeed += MCSspeed
            speedCounter += 1

        # reset vars for next MCS in list
        aaveragePropagationSpeed = 0.0
        averageArea = 0.0
        averageAreaCounter = 0
        durationOfMatureMCC = 0
        MCSspeed = 0.0
        MCSspeedCounter = 0
        MCSPrecipTotal = 0.0
        avgMaxMCSPrecipRate = 0.0
        avgMaxMCSPrecipRateCounter = 0
        avgMinMCSPrecipRate = 0.0
        avgMinMCSPrecipRateCounter = 0
        firstTime = True
        matureFlag = True
        avgMCSPrecipTotalCounter = 0
        avgPrecipAreaPercent = 0.0
        precipArea = 0.0
        precipCounter = 0
        maxArea = 0.0
        maxAreaTime = ''
        eccentricity = 0.0
        timeMCSMatures = ''
        maxCEprecipRate = 0.0
        minCEprecipRate = 0.0
        location = []

    # LD: average duration
    if len(finalMCCList) > 1:
        durations /= len(finalMCCList)
        durations /= 3600.0  # convert to hours

        # A: average area
        areaAvg = sum(averageAreas) / len(finalMCCList)
    # create histogram plot here
    if len(averageAreas) > 1:
        imgFilename = MAINDIRECTORY + '/images/averageAreas.gif'
        plotter.draw_histogram(
            averageAreas, [
                "Average Area [km^2]", "Area [km^2]"], imgFilename, 10)

    # Amax: average maximum area
    if maxAreaCounter > 0.0:  # and avgMaxArea > 0.0 :
        amax = sum(avgMaxArea) / maxAreaCounter
        # create histogram plot here
        if len(avgMaxArea) > 1:
            imgFilename = MAINDIRECTORY + '/images/avgMaxArea.gif'
            plotter.draw_histogram(
                avgMaxArea, [
                    "Maximum Area [km^2]", "Area [km^2]"], imgFilename, 10)

    # v_avg: calculate the average propagation speed
    if speedCounter > 0:  # and averagePropagationSpeed > 0.0
        averagePropagationSpeed /= speedCounter

    # bigP_min: calculate the min rate in mature system
    if avgMinPrecipRate > 0.0:  # and avgMinPrecipRateCounter > 0.0:
        avgMinPrecipRate /= avgMinPrecipRateCounter

    # bigP_max: calculate the max rate in mature system
    if avgMinPrecipRateCounter > 0.0:  # and avgMaxPrecipRate >  0.0:
        avgMaxPrecipRate /= avgMaxPrecipRateCounter

    # bigP_avg: average total preicip rate mm/hr
    if avgPrecipTotalCounter > 0.0:  # and avgPrecipTotal > 0.0:
        avgPrecipTotal /= avgPrecipTotalCounter

    # bigP_total: total precip rate mm/LD
    if bigPtotalCounter > 0.0:  # and bigPtotal > 0.0:
        bigPtotal /= bigPtotalCounter

    # precipitation area percentage
    if len(precipPercent) > 0:
        precipAreaPercent = (sum(precipPercent) / len(precipPercent)) * 100.0

    # average precipitation area
    if len(avgPrecipArea) > 0:
        precipAreaAvg = sum(avgPrecipArea) / len(avgPrecipArea)
        if len(avgPrecipArea) > 1:
            imgFilename = MAINDIRECTORY + '/images/avgPrecipArea.gif'
            plotter.draw_histogram(
                avgPrecipArea, [
                    "Average Rainfall Area [km^2]", "Area [km^2]"], imgFilename, 10)

    sTime = str(averageTime(startTimes))
    eTime = str(averageTime(endTimes))
    if len(allPropagationSpeeds) > 1:
        maxSpeed = max(allPropagationSpeeds)
        minSpeed = min(allPropagationSpeeds)

    # write stuff to the summary file
    MCSSummaryFile.write("\nNumber of features is %d " % (len(finalMCCList)))
    MCSSummaryFile.write("\nAverage duration is %.4f hrs " % (durations))
    MCSSummaryFile.write("\nAverage startTime is %s " % (sTime[-8:]))
    MCSSummaryFile.write("\nAverage endTime is %s " % (eTime[-8:]))
    MCSSummaryFile.write("\nAverage size is %.4f km^2 " % (areaAvg))
    MCSSummaryFile.write(
        "\nAverage precipitation area is %.4f km^2 " %
        (precipAreaAvg))
    MCSSummaryFile.write("\nAverage maximum size is %.4f km^2 " % (amax))
    MCSSummaryFile.write(
        "\nAverage propagation speed is %.4f ms^-1" %
        (averagePropagationSpeed))
    MCSSummaryFile.write(
        "\nMaximum propagation speed is %.4f ms^-1 " %
        (maxSpeed))
    MCSSummaryFile.write(
        "\nMinimum propagation speed is %.4f ms^-1 " %
        (minSpeed))
    MCSSummaryFile.write(
        "\nAverage minimum precipitation rate is %.4f mmh^-1" %
        (avgMinPrecipRate))
    MCSSummaryFile.write(
        "\nAverage maximum precipitation rate is %.4f mm h^-1" %
        (avgMaxPrecipRate))
    MCSSummaryFile.write(
        "\nAverage precipitation is %.4f mm h^-1 " %
        (avgPrecipTotal))
    MCSSummaryFile.write(
        "\nAverage total precipitation during MCSs is %.4f mm/LD " %
        (bigPtotal))
    MCSSummaryFile.write(
        "\nAverage precipitation area percentage is %.4f percent " %
        (precipAreaPercent))

    MCSUserFile.close
    MCSSummaryFile.close
    MCSPostFile.close
    return
#******************************************************************
#			PLOTTING UTIL SCRIPTS
#******************************************************************


def to_percent(y, position):
    '''
    Purpose::
            Utility script for generating the y-axis for plots
    '''
    return (str(100 * y) + '%')
#******************************************************************


def colorbar_index(ncolors, nlabels, cmap):
    '''
    Purpose::
            Utility script for crating a colorbar
            Taken from http://stackoverflow.com/questions/18704353/correcting-matplotlib-colorbar-ticks

    '''
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors + 0.5)
    colorbar = plt.colorbar(mappable)  # , orientation='horizontal')
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(nlabels)
    return
#******************************************************************


def cmap_discretize(cmap, N):
    '''
    Taken from: http://stackoverflow.com/questions/18704353/correcting-matplotlib-colorbar-ticks
    http://wiki.scipy.org/Cookbook/Matplotlib/ColormapTransformations
    Return a discrete colormap from the continuous colormap cmap.

            cmap: colormap instance, eg. cm.jet.
            N: number of colors.

    Example
            x = resize(arange(100), (5,100))
            djet = cmap_discretize(cm.jet, 5)
            imshow(x, cmap=djet)
    '''

    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki])
                      for i in range(N + 1)]
    # Return colormap object.
    return mcolors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)
#******************************************************************
# def preprocessingMERG(MERGdirname):
# 	'''
# 	Purpose::
# 		Utility script for unzipping and converting the merg*.Z files from Mirador to
# 		NETCDF format. The files end up in a folder called mergNETCDF in the directory
# 		where the raw MERG data is
# 		NOTE: VERY RAW AND DIRTY
# 	Input::
# 		Directory to the location of the raw MERG files, preferably zipped
# 	Output::
# 	   none
# 	Assumptions::
# 	   1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
# 		 have been installed on the system and the user can access
# 	   2 User can write files in location where script is being called
# 	   3 the files havent been unzipped
# 	'''

# 	os.chdir((MERGdirname+'/'))
# 	imgFilename = ''

# 	#Just incase the X11 server is giving problems
# 	subprocess.call('export DISPLAY=:0.0', shell=True)

# 	for files in glob.glob("*-pixel"):
# 	#for files in glob.glob("*.Z"):
# 		fname = os.path.splitext(files)[0]

# 		#unzip it
# 		bash_cmd = 'gunzip ' + files
# 		subprocess.call(bash_cmd, shell=True)

# 		#determine the time from the filename
# 		ftime = re.search('\_(.*)\_',fname).group(1)

# 		yy = ftime[0:4]
# 		mm = ftime[4:6]
# 		day = ftime[6:8]
# 		hr = ftime [8:10]

# 		#TODO: must be something more efficient!

# 		if mm=='01':
# 			mth = 'Jan'
# 		if mm == '02':
# 			mth = 'Feb'
# 		if mm == '03':
# 			mth = 'Mar'
# 		if mm == '04':
# 			mth = 'Apr'
# 		if mm == '05':
# 			mth = 'May'
# 		if mm == '06':
# 			mth = 'Jun'
# 		if mm == '07':
# 			mth = 'Jul'
# 		if mm == '08':
# 			mth = 'Aug'
# 		if mm == '09':
# 			mth = 'Sep'
# 		if mm == '10':
# 			mth = 'Oct'
# 		if mm == '11':
# 			mth = 'Nov'
# 		if mm == '12':
# 			mth = 'Dec'


# 		subprocess.call('rm merg.ctl', shell=True)
# 		subprocess.call('touch merg.ctl', shell=True)
# 		replaceExpDset = 'echo DSET ' + fname +' >> merg.ctl'
# 		replaceExpTdef = 'echo TDEF 99999 LINEAR '+hr+'z'+day+mth+yy +' 30mn' +' >> merg.ctl'
# 		subprocess.call(replaceExpDset, shell=True)
# 		subprocess.call('echo "OPTIONS yrev little_endian template" >> merg.ctl', shell=True)
# 		subprocess.call('echo "UNDEF  330" >> merg.ctl', shell=True)
# 		subprocess.call('echo "TITLE  globally merged IR data" >> merg.ctl', shell=True)
# 		subprocess.call('echo "XDEF 9896 LINEAR   0.0182 0.036378335" >> merg.ctl', shell=True)
# 		subprocess.call('echo "YDEF 3298 LINEAR   -59.982 0.036383683" >> merg.ctl', shell=True)
# 		subprocess.call('echo "ZDEF   01 LEVELS 1" >> merg.ctl', shell=True)
# 		subprocess.call(replaceExpTdef, shell=True)
# 		subprocess.call('echo "VARS 1" >> merg.ctl', shell=True)
# 		subprocess.call('echo "ch4  1  -1,40,1,-1 IR BT  (add  "75" to this value)" >> merg.ctl', shell=True)
# 		subprocess.call('echo "ENDVARS" >> merg.ctl', shell=True)

# 		#generate the lats4D command for GrADS
# 		lats4D = 'lats4d -v -q -lat '+LATMIN + ' ' +LATMAX +' -lon ' +LONMIN +' ' +LONMAX +' -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname

# 		#lats4D = 'lats4d -v -q -lat -40 -15 -lon 10 40 -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname
# 		#lats4D = 'lats4d -v -q -lat -5 40 -lon -90 60 -func @+75 ' + '-i merg.ctl' + ' -o ' + fname

# 		gradscmd = 'grads -blc ' + '\'' +lats4D + '\''
# 		#run grads and lats4d command
# 		subprocess.call(gradscmd, shell=True)
# 		imgFilename = hr+'Z'+day+mth+yy+'.gif'
# 		tempMaskedImages(imgFilename)

# 	#when all the files have benn converted, mv the netcdf files
# 	subprocess.call('mkdir mergNETCDF', shell=True)
# 	subprocess.call('mv *.nc mergNETCDF', shell=True)
# 	#mv all images
# 	subprocess.call('mkdir mergImgs', shell=True)
# 	subprocess.call('mv *.gif mergImgs', shell=True)
# 	return
