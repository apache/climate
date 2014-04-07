'''
# All the functions for the MCC search algorithm
# Following RCMES dataformat in format (t,lat,lon), value
# Kim Whitehall 
# Mimumum MCS is 3 hours
'''

import datetime
from datetime import timedelta, datetime
import calendar
import fileinput
import glob
import itertools
import json
import math
import Nio
from netCDF4 import Dataset, num2date, date2num
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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter,HourLocator 
from matplotlib import cm
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter, FormatStrFormatter

#existing modules in services
import files
import process
#----------------------- GLOBAL VARIABLES --------------------------
# --------------------- User defined variables ---------------------
#FYI the lat lon values are not necessarily inclusive of the points given. These are the limits
#the first point closest the the value (for the min) from the MERG data is used, etc.
LATMIN = '5.0' #'12.0' #'-40' #'12.0'  #'10.0' #'-40.0' #'-5.0' 		#min latitude; -ve values in the SH e.g. 5S = -5
LATMAX = '19.0' #'17.0' #'-20.0' #'17.0' #'20.0' #'30.0'			#max latitude; -ve values in the SH e.g. 5S = -5 20.0
LONMIN = '-9.0' #'-8.0' #'10.0' #'-8.0' #'-5.0' #'10.0' #'-40.0'		#min longitude; -ve values in the WH e.g. 59.8W = -59.8 -30
LONMAX = '5.0' #'8.0' #'40.0' #'8.0' #'40.0' #'5.0'			#min longitude; -ve values in the WH e.g. 59.8W = -59.8  30
XRES = 4.0				#x direction spatial resolution in km
YRES = 4.0				#y direction spatial resolution in km
TRES = 1 				#temporal resolution in hrs
T_BB_MAX = 243 #241   		#warmest temp to allow (-30C to -55C according to Morel and Sensi 2002)
T_BB_MIN = 218 #221		    #cooler temp for the center of the system
STRUCTURING_ELEMENT = [[0,1,0],[1,1,1],[0,1,0]] #the matrix for determining the pattern for the contiguous boxes and must
    											#have same rank of the matrix it is being compared against 
CONVECTIVE_FRACTION = 0.90 #the min temp/max temp that would be expected in a CE.. this is highly conservative (only a 10K difference)
MIN_MCS_DURATION = 3    #minimum time for a MCS to exist
MIN_CE_SPEED = 45.0 	#the slowest speed a CE can move btwn F for the resolved data in kmhr^-1.here is hrly, therefore val 
MAX_CE_SPEED = 70.0 	#the fastest speed a CE can move btwn F for the resolved data in kmhr^-1.
LAT_DISTANCE = 111.0 	#the avg distance in km for 1deg lat for the region being considered 
LON_DISTANCE = 111.0    #the avg distance in km for 1deg lon for the region being considered
DIRECTION = 45.0 		#general direction of the wind flow in degrees
AREA_MIN = 2400.0		#minimum area for CE criteria in km^2 according to Vila et al. (2008) is 2400
MIN_OVERLAP= 10000.00      #km^2  from Williams and Houze 1987, indir ref in Arnaud et al 1992

#---Assuming using the MCC function, these will have to be changed  
ECCENTRICITY_THRESHOLD_MAX = 1.0  #tending to 1 is a circle e.g. hurricane, 
ECCENTRICITY_THRESHOLD_MIN = 0.70 #0.65  #tending to 0 is a linear e.g. squall line
OUTER_CLOUD_SHIELD_AREA = 80000.0 #100000.0 #km^2
INNER_CLOUD_SHIELD_AREA = 30000.0 #50000.0 #km^2
OUTER_CLOUD_SHIELD_TEMPERATURE = 233 #in K
INNER_CLOUD_SHIELD_TEMPERATURE = 213 #in K
MINIMUM_DURATION = 6 #min number of frames the MCC must exist for (assuming hrly frames, African MCCs is 6hrs)
MAXIMUM_DURATION = 100 #max number of framce the MCC can last for (assuming hrly frames, African MCCs last at most 15hrs)

#MAINDIRECTORY = "/Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1"
#------------------- End user defined Variables -------------------
edgeWeight = [1,2,3] #weights for the graph edges
#graph object fo the CEs meeting the criteria
CLOUD_ELEMENT_GRAPH = nx.DiGraph()
#graph meeting the CC criteria
PRUNED_GRAPH = nx.DiGraph()
#------------------------ End GLOBAL VARS -------------------------
#************************ Begin Functions *************************
#******************************************************************
def readMergData(dirname):
	'''
	Purpose::
	    Read MERG data into RCMES format
	
	Input::
	    Directory to the MERG files in NETCDF format
	
	Output::
	    A 3D masked array (t,lat,lon) with only the variables which meet the minimum temperature 
	    criteria for each frame
	    **remove below**
	    A dictionary of all the MERG data from the files in the directory given.
	    The dictionary contains, a string representing the time (a datetime string), a 
	    tuple (lat,lon,value) representing only the data that meets the temperature requirements
	    i.e. T_BB_MAX

	Assumptions::
	    The MERG data has been converted to NETCDF using LATS4D
	    The data has the same lat/lon format
	'''

	global LAT
	global LON

	# these strings are specific to the MERG data
	mergVarName = 'ch4'
	mergTimeVarName = 'time'
	mergLatVarName = 'latitude'
	mergLonVarName = 'longitude'
	
	filelistInstructions = dirname + '/*'
	filelist = glob.glob(filelistInstructions)

	
	#sat_img is the array that will contain all the masked frames
	mergImgs = []
	#timelist of python time strings
	timelist = [] 
	time2store = None
	tempMaskedValueNp =[]
	

	filelist.sort()
	nfiles = len(filelist)

	# Crash nicely if there are no netcdf files
	if nfiles == 0:
		print 'Error: no files in this directory! Exiting elegantly'
		sys.exit()
	else:
		# Open the first file in the list to read in lats, lons and generate the  grid for comparison
		tmp = Nio.open_file(filelist[0], format='nc')
		#TODO: figure out how to use netCDF4 to do the clipping tmp = netCDF4.Dataset(filelist[0])

		#clip the lat/lon grid according to user input
		#http://www.pyngl.ucar.edu/NioExtendedSelection.shtml
		latsraw = tmp.variables[mergLatVarName][mergLatVarName+"|"+LATMIN+":"+LATMAX].astype('f2')
		lonsraw = tmp.variables[mergLonVarName][mergLonVarName+"|"+LONMIN+":"+LONMAX].astype('f2')
		lonsraw[lonsraw > 180] = lonsraw[lonsraw > 180] - 360.  # convert to -180,180 if necessary
		
		LON, LAT = np.meshgrid(lonsraw, latsraw)
		#clean up
		latsraw =[]
		lonsraw = []
		nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])
		#print 'Lats and lons read in for first file in filelist',nygrd,nxgrd
		tmp.close
	
	for files in filelist:
		try:
			thisFile = Nio.open_file(files, format='nc') 
			#TODO: thisFile = netCDF4.Dataset(files)

			#clip the dataset according to user lat,lon coordinates
			#mask the data and fill with zeros for later 
			tempRaw = thisFile.variables[mergVarName][mergLatVarName+"|"+LATMIN+":"+LATMAX \
			                           +" " +mergLonVarName+"|"+LONMIN+":"+LONMAX ].astype('int16')

			tempMask = ma.masked_array(tempRaw, mask=(tempRaw > T_BB_MAX), fill_value=0) 
			
			#get the actual values that the mask returned
			tempMaskedValue = ma.zeros((tempRaw.shape)).astype('int16')
			for index, value in maenumerate(tempMask): 
				time_index, lat_index, lon_index = index			
				tempMaskedValue[time_index,lat_index, lon_index]=value	
				
			timesRaw = thisFile.variables[mergTimeVarName]
			#convert this time to a python datastring
			time2store, _ = process.getModelTimes(files, mergTimeVarName)
			#extend instead of append because getModelTimes returns a list already and we don't 
			#want a list of list
			timelist.extend(time2store)
			#to get the actual masked data only
			#http://docs.scipy.org/doc/numpy/reference/maskedarray.generic.html#accessing-only-the-valid-entries
			mergImgs.extend(tempMaskedValue) 
			thisFile.close
			thisFile = None
			
		except:
			print "bad file! ", file

	mergImgs = ma.array(mergImgs)

	return mergImgs, timelist
#******************************************************************
def findCloudElements(mergImgs,timelist,TRMMdirName=None):
	'''
	Purpose::
	    Determines the contiguous boxes for a given time of the satellite images i.e. each frame
        using scipy ndimage package
	
	Input::
	    3 variables
		sat_img: masked numpy array in (time,lat,lon),T_bb representing the satellite data. This is masked based on the
		maximum acceptable temperature, T_BB_MAX
		timelist: a list of python datatimes
		TRMMdirName (optional): string representing the path where to find the TRMM datafiles
		
	Output::
	    1 variable
		cloudEements: list of dictionary of cloudElements which have met the temperature, area and shape requirements
		The dictionary is 
		cloudElementDict = {'uniqueID': unique tag for this CE, 
							'cloudElementTime': time of the CE,
							'cloudElementLatLon': (lat,lon,value) of MERG data of CE, 
							'cloudElementCenter':tuple of floating-point (lat,lon) representing the CE's center 
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

	frame = ma.empty((1,mergImgs.shape[1],mergImgs.shape[2]))
	CEcounter = 0
	frameCEcounter = 0
	frameNum = 0
	cloudElementEpsilon = 0.0
	cloudElementDict = {} 
	cloudElementCenter = []		#list with two elements [lat,lon] for the center of a CE
	prevFrameCEs = []			#list for CEs in previous frame
	currFrameCEs = []			#list for CEs in current frame
	cloudElementLat = []		#list for a particular CE's lat values
	cloudElementLon = []		#list for a particular CE's lon values
	cloudElementLatLons = []	#list for a particular CE's (lat,lon) values
	
	prevLatValue = 0.0
	prevLonValue = 0.0
	TIR_min = 0.0
	TIR_max = 0.0
	temporalRes = 3 # TRMM data is 3 hourly
	precipTotal = 0.0
	CETRMMList =[]
	precip =[]
	TRMMCloudElementLatLons =[]

	#edgeWeight = [1,2]
	minCELatLimit = 0.0
	minCELonLimit = 0.0
	maxCELatLimit = 0.0
	maxCELonLimit = 0.0
	
	nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])
	
	#openfile for storing ALL cloudElement information 
	cloudElementsFile = open((MAINDIRECTORY+'/textFiles/cloudElements.txt'),'wb')


	#openfile for storing cloudElement information meeting user criteria i.e. MCCs in this case
	cloudElementsUserFile = open((MAINDIRECTORY+'/textFiles/cloudElementsUserFile.txt'),'w')
	#cloudElementsTextFile = open('/Users/kimwhitehall/Documents/HU/research/mccsearch/cloudElementsTextFile.txt','w')

	#NB in the TRMM files the info is hours since the time thus 00Z file has in 01, 02 and 03 times
	for t in xrange(mergImgs.shape[0]):
		#-------------------------------------------------
		# #textfile name for saving the data for arcgis
		# thisFileName = MAINDIRECTORY+'/' + (str(timelist[t])).replace(" ", "_") + '.txt'
		# cloudElementsTextFile = open(thisFileName,'w')
		#-------------------------------------------------

		#determine contiguous locations with temeperature below the warmest temp i.e. cloudElements in each frame
	   	frame, CEcounter = ndimage.measurements.label(mergImgs[t,:,:], structure=STRUCTURING_ELEMENT)
	   	frameCEcounter=0
		frameNum += 1

		#for each of the areas identified, check to determine if it a valid CE via an area and T requirement
	   	for count in xrange(CEcounter):
	   		#[0] is time dimension. Determine the actual values from the data
	   		#loc is a masked array
	   		try:
	   			loc = ndimage.find_objects(frame==(count+1))[0]
	   		except Exception, e:
	   			print "Error is ", e
	   			continue


	   		cloudElement = mergImgs[t,:,:][loc]
	   		labels, lcounter = ndimage.label(cloudElement)
	   		
	   		#determine the true lats and lons for this particular CE
   			cloudElementLat = LAT[loc[0],0]
   			cloudElementLon = LON[0,loc[1]] 
   			
	   		#determine number of boxes in this cloudelement
	   		numOfBoxes = np.count_nonzero(cloudElement)
	   		cloudElementArea = numOfBoxes*XRES*YRES

	   		#If the area is greater than the area required, then start considering as CE
	   		#TODO: if the area is smaller than the suggested area, check if it meets a convective fraction requirement
	   		#if it does, still consider as CE

	   		if cloudElementArea >= AREA_MIN or (cloudElementArea < AREA_MIN and ((ndimage.minimum(cloudElement, labels=labels))/float((ndimage.maximum(cloudElement, labels=labels)))) < CONVECTIVE_FRACTION ):

	   			#get some time information and labeling info
	   			frameTime = str(timelist[t])
	   			frameCEcounter +=1
	   			CEuniqueID = 'F'+str(frameNum)+'CE'+str(frameCEcounter) 

	   			#-------------------------------------------------
	    		#textfile name for accesing CE data using MATLAB code
				# thisFileName = MAINDIRECTORY+'/' + (str(timelist[t])).replace(" ", "_") + CEuniqueID +'.txt'
				# cloudElementsTextFile = open(thisFileName,'w')
				#-------------------------------------------------

				# ------ NETCDF File stuff for brightness temp stuff ------------------------------------
				thisFileName = MAINDIRECTORY +'/MERGnetcdfCEs/cloudElements'+ (str(timelist[t])).replace(" ", "_") + CEuniqueID +'.nc'
				currNetCDFCEData = Dataset(thisFileName, 'w', format='NETCDF4')
				currNetCDFCEData.description = 'Cloud Element '+CEuniqueID + ' temperature data'
				currNetCDFCEData.calendar = 'standard'
				currNetCDFCEData.conventions = 'COARDS'
				# dimensions
				currNetCDFCEData.createDimension('time', None)
				currNetCDFCEData.createDimension('lat', len(LAT[:,0]))
				currNetCDFCEData.createDimension('lon', len(LON[0,:]))
				# variables
				tempDims = ('time','lat', 'lon',)
				times = currNetCDFCEData.createVariable('time', 'f8', ('time',))
				times.units = 'hours since '+ str(timelist[t])[:-6]
				latitudes = currNetCDFCEData.createVariable('latitude', 'f8', ('lat',))
				longitudes = currNetCDFCEData.createVariable('longitude', 'f8', ('lon',))
				brightnesstemp = currNetCDFCEData.createVariable('brightnesstemp', 'i16',tempDims )
				brightnesstemp.units = 'Kelvin'
				# NETCDF data
				dates=[timelist[t]+timedelta(hours=0)]
				times[:] =  date2num(dates,units=times.units)
				longitudes[:] = LON[0,:]
				longitudes.units = "degrees_east" 
				longitudes.long_name = "Longitude" 

				latitudes[:] =  LAT[:,0]
				latitudes.units = "degrees_north"
				latitudes.long_name ="Latitude"
				
				#generate array of zeros for brightness temperature
				brightnesstemp1 = ma.zeros((1,len(latitudes), len(longitudes))).astype('int16')
				#-----------End most of NETCDF file stuff ------------------------------------

				#if other dataset (TRMM) assumed to be a precipitation dataset was entered
				if TRMMdirName:
					#------------------TRMM stuff -------------------------------------------------
					fileDate = ((str(timelist[t])).replace(" ", "")[:-8]).replace("-","")
					fileHr1 = (str(timelist[t])).replace(" ", "")[-8:-6]
					
					if int(fileHr1) % temporalRes == 0:
						fileHr = fileHr1
					else:
						fileHr = (int(fileHr1)/temporalRes) * temporalRes
					if fileHr < 10:
						fileHr = '0'+str(fileHr)
					else:
						str(fileHr)

					#open TRMM file for the resolution info and to create the appropriate sized grid
					TRMMfileName = TRMMdirName+'/3B42.'+ fileDate + "."+str(fileHr)+".7A.nc"
					
					TRMMData = Dataset(TRMMfileName,'r', format='NETCDF4')
					precipRate = TRMMData.variables['pcp'][:,:,:]
					latsrawTRMMData = TRMMData.variables['latitude'][:]
					lonsrawTRMMData = TRMMData.variables['longitude'][:]
					lonsrawTRMMData[lonsrawTRMMData > 180] = lonsrawTRMMData[lonsrawTRMMData>180] - 360.
					LONTRMM, LATTRMM = np.meshgrid(lonsrawTRMMData, latsrawTRMMData)

					nygrdTRMM = len(LATTRMM[:,0]); nxgrdTRMM = len(LONTRMM[0,:])
					precipRateMasked = ma.masked_array(precipRate, mask=(precipRate < 0.0))
					#---------regrid the TRMM data to the MERG dataset ----------------------------------
					#regrid using the do_regrid stuff from the Apache OCW 
					regriddedTRMM = ma.zeros((0, nygrd, nxgrd))
					regriddedTRMM = process.do_regrid(precipRateMasked[0,:,:], LATTRMM,  LONTRMM, LAT, LON, order=1, mdi= -999999999)
					#----------------------------------------------------------------------------------
		
					# #get the lat/lon info from cloudElement
					#get the lat/lon info from the file
					latCEStart = LAT[0][0]
					latCEEnd = LAT[-1][0]
					lonCEStart = LON[0][0]
					lonCEEnd = LON[0][-1]
					
					#get the lat/lon info for TRMM data (different resolution)
					latStartT = find_nearest(latsrawTRMMData, latCEStart)
					latEndT = find_nearest(latsrawTRMMData, latCEEnd)
					lonStartT = find_nearest(lonsrawTRMMData, lonCEStart)
					lonEndT = find_nearest(lonsrawTRMMData, lonCEEnd)
					latStartIndex = np.where(latsrawTRMMData == latStartT)
					latEndIndex = np.where(latsrawTRMMData == latEndT)
					lonStartIndex = np.where(lonsrawTRMMData == lonStartT)
					lonEndIndex = np.where(lonsrawTRMMData == lonEndT)

					#get the relevant TRMM info 
					CEprecipRate = precipRate[:,(latStartIndex[0][0]-1):latEndIndex[0][0],(lonStartIndex[0][0]-1):lonEndIndex[0][0]]
					TRMMData.close()
					
					# ------ NETCDF File info for writing TRMM CE rainfall ------------------------------------
					thisFileName = MAINDIRECTORY+'/TRMMnetcdfCEs/TRMM' + (str(timelist[t])).replace(" ", "_") + CEuniqueID +'.nc'
					currNetCDFTRMMData = Dataset(thisFileName, 'w', format='NETCDF4')
					currNetCDFTRMMData.description = 'Cloud Element '+CEuniqueID + ' precipitation data'
					currNetCDFTRMMData.calendar = 'standard'
					currNetCDFTRMMData.conventions = 'COARDS'
					# dimensions
					currNetCDFTRMMData.createDimension('time', None)
					currNetCDFTRMMData.createDimension('lat', len(LAT[:,0]))
					currNetCDFTRMMData.createDimension('lon', len(LON[0,:]))
					
					# variables
					TRMMprecip = ('time','lat', 'lon',)
					times = currNetCDFTRMMData.createVariable('time', 'f8', ('time',))
					times.units = 'hours since '+ str(timelist[t])[:-6]
					latitude = currNetCDFTRMMData.createVariable('latitude', 'f8', ('lat',))
					longitude = currNetCDFTRMMData.createVariable('longitude', 'f8', ('lon',))
					rainFallacc = currNetCDFTRMMData.createVariable('precipitation_Accumulation', 'f8',TRMMprecip )
					rainFallacc.units = 'mm'

					longitude[:] = LON[0,:]
					longitude.units = "degrees_east" 
					longitude.long_name = "Longitude" 

					latitude[:] =  LAT[:,0]
					latitude.units = "degrees_north"
					latitude.long_name ="Latitude"

					finalCETRMMvalues = ma.zeros((brightnesstemp.shape))
					#-----------End most of NETCDF file stuff ------------------------------------

	   			#populate cloudElementLatLons by unpacking the original values from loc to get the actual value for lat and lon
    			#TODO: KDW - too dirty... play with itertools.izip or zip and the enumerate with this
    			# 			as cloudElement is masked
				for index,value in np.ndenumerate(cloudElement):
					if value != 0 : 
						lat_index,lon_index = index
						lat_lon_tuple = (cloudElementLat[lat_index], cloudElementLon[lon_index],value)

						#generate the comma separated file for GIS
						cloudElementLatLons.append(lat_lon_tuple)

						#temp data for CE NETCDF file
						brightnesstemp1[0,int(np.where(LAT[:,0]==cloudElementLat[lat_index])[0]),int(np.where(LON[0,:]==cloudElementLon[lon_index])[0])] = value
						
						if TRMMdirName:
							finalCETRMMvalues[0,int(np.where(LAT[:,0]==cloudElementLat[lat_index])[0]),int(np.where(LON[0,:]==cloudElementLon[lon_index])[0])] = regriddedTRMM[int(np.where(LAT[:,0]==cloudElementLat[lat_index])[0]),int(np.where(LON[0,:]==cloudElementLon[lon_index])[0])]
							CETRMMList.append((cloudElementLat[lat_index], cloudElementLon[lon_index], finalCETRMMvalues[0,cloudElementLat[lat_index], cloudElementLon[lon_index]]))


				brightnesstemp[:] = brightnesstemp1[:]
				currNetCDFCEData.close()

				if TRMMdirName:

					#calculate the total precip associated with the feature
					for index, value in np.ndenumerate(finalCETRMMvalues):
						precipTotal += value 
	    				precip.append(value)
			
					rainFallacc[:] = finalCETRMMvalues[:]
					currNetCDFTRMMData.close()
					TRMMnumOfBoxes = np.count_nonzero(finalCETRMMvalues)
					TRMMArea = TRMMnumOfBoxes*XRES*YRES
					try:
						maxCEprecipRate = np.max(finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
						minCEprecipRate = np.min(finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
					except:
						pass

				#sort cloudElementLatLons by lats
				cloudElementLatLons.sort(key=lambda tup: tup[0])	

				#determine if the cloud element the shape 
				cloudElementEpsilon = eccentricity (cloudElement)
	   			cloudElementsUserFile.write("\n\nTime is: %s" %(str(timelist[t])))
	   			cloudElementsUserFile.write("\nCEuniqueID is: %s" %CEuniqueID)
	   			latCenter, lonCenter = ndimage.measurements.center_of_mass(cloudElement, labels=labels)
	   			
	   			#latCenter and lonCenter are given according to the particular array defining this CE
	   			#so you need to convert this value to the overall domain truth
	   			latCenter = cloudElementLat[round(latCenter)]
	   			lonCenter = cloudElementLon[round(lonCenter)]
	   			cloudElementsUserFile.write("\nCenter (lat,lon) is: %.2f\t%.2f" %(latCenter, lonCenter))
	   			cloudElementCenter.append(latCenter)
	   			cloudElementCenter.append(lonCenter)
	   			cloudElementsUserFile.write("\nNumber of boxes are: %d" %numOfBoxes)
	   			cloudElementsUserFile.write("\nArea is: %.4f km^2" %(cloudElementArea))
				cloudElementsUserFile.write("\nAverage brightness temperature is: %.4f K" %ndimage.mean(cloudElement, labels=labels))
				cloudElementsUserFile.write("\nMin brightness temperature is: %.4f K" %ndimage.minimum(cloudElement, labels=labels))
				cloudElementsUserFile.write("\nMax brightness temperature is: %.4f K" %ndimage.maximum(cloudElement, labels=labels))
				cloudElementsUserFile.write("\nBrightness temperature variance is: %.4f K" %ndimage.variance(cloudElement, labels=labels))
				cloudElementsUserFile.write("\nConvective fraction is: %.4f " %(((ndimage.minimum(cloudElement, labels=labels))/float((ndimage.maximum(cloudElement, labels=labels))))*100.0))
				cloudElementsUserFile.write("\nEccentricity is: %.4f " %(cloudElementEpsilon))
				#populate the dictionary
				if TRMMdirName:
					cloudElementDict = {'uniqueID': CEuniqueID, 'cloudElementTime': timelist[t],'cloudElementLatLon': cloudElementLatLons, 'cloudElementCenter':cloudElementCenter, 'cloudElementArea':cloudElementArea, 'cloudElementEccentricity':cloudElementEpsilon, 'cloudElementTmax':TIR_max, 'cloudElementTmin': TIR_min, 'cloudElementPrecipTotal':precipTotal,'cloudElementLatLonTRMM':CETRMMList, 'TRMMArea': TRMMArea,'CETRMMmax':maxCEprecipRate, 'CETRMMmin':minCEprecipRate}
				else:
					cloudElementDict = {'uniqueID': CEuniqueID, 'cloudElementTime': timelist[t],'cloudElementLatLon': cloudElementLatLons, 'cloudElementCenter':cloudElementCenter, 'cloudElementArea':cloudElementArea, 'cloudElementEccentricity':cloudElementEpsilon, 'cloudElementTmax':TIR_max, 'cloudElementTmin': TIR_min,}
				
				#current frame list of CEs
				currFrameCEs.append(cloudElementDict)
				
				#draw the graph node
				CLOUD_ELEMENT_GRAPH.add_node(CEuniqueID, cloudElementDict)
				
				if frameNum != 1:
					for cloudElementDict in prevFrameCEs:
						thisCElen = len(cloudElementLatLons)
						percentageOverlap, areaOverlap = cloudElementOverlap(cloudElementLatLons, cloudElementDict['cloudElementLatLon'])
						
						#change weights to integers because the built in shortest path chokes on floating pts
						#according to Goyens et al, two CEs are considered related if there is atleast 95% overlap between them for consecutive imgs a max of 2 hrs apart
						if percentageOverlap >= 0.95: 
							CLOUD_ELEMENT_GRAPH.add_edge(cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[0])
							
						elif percentageOverlap >= 0.90 and percentageOverlap < 0.95 :
							CLOUD_ELEMENT_GRAPH.add_edge(cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[1])

						elif areaOverlap >= MIN_OVERLAP:
							CLOUD_ELEMENT_GRAPH.add_edge(cloudElementDict['uniqueID'], CEuniqueID, weight=edgeWeight[2])

    			else:
    				#TODO: remove this else as we only wish for the CE details
    				#ensure only the non-zero elements are considered
    				#store intel in allCE file
    				labels, _ = ndimage.label(cloudElement)
    				cloudElementsFile.write("\n-----------------------------------------------")
    				cloudElementsFile.write("\n\nTime is: %s" %(str(timelist[t])))
    				# cloudElementLat = LAT[loc[0],0]
    				# cloudElementLon = LON[0,loc[1]] 
    				
    				#populate cloudElementLatLons by unpacking the original values from loc
    				#TODO: KDW - too dirty... play with itertools.izip or zip and the enumerate with this
    				# 			as cloudElement is masked
    				for index,value in np.ndenumerate(cloudElement):
    					if value != 0 : 
    						lat_index,lon_index = index
    						lat_lon_tuple = (cloudElementLat[lat_index], cloudElementLon[lon_index])
    						cloudElementLatLons.append(lat_lon_tuple)
	
    				cloudElementsFile.write("\nLocation of rejected CE (lat,lon) points are: %s" %cloudElementLatLons)
    				#latCenter and lonCenter are given according to the particular array defining this CE
		   			#so you need to convert this value to the overall domain truth
    				latCenter, lonCenter = ndimage.measurements.center_of_mass(cloudElement, labels=labels)
    				latCenter = cloudElementLat[round(latCenter)]
    				lonCenter = cloudElementLon[round(lonCenter)]
    				cloudElementsFile.write("\nCenter (lat,lon) is: %.2f\t%.2f" %(latCenter, lonCenter))
    				cloudElementsFile.write("\nNumber of boxes are: %d" %numOfBoxes)
    				cloudElementsFile.write("\nArea is: %.4f km^2" %(cloudElementArea))
    				cloudElementsFile.write("\nAverage brightness temperature is: %.4f K" %ndimage.mean(cloudElement, labels=labels))
    				cloudElementsFile.write("\nMin brightness temperature is: %.4f K" %ndimage.minimum(cloudElement, labels=labels))
    				cloudElementsFile.write("\nMax brightness temperature is: %.4f K" %ndimage.maximum(cloudElement, labels=labels))
    				cloudElementsFile.write("\nBrightness temperature variance is: %.4f K" %ndimage.variance(cloudElement, labels=labels))
    				cloudElementsFile.write("\nConvective fraction is: %.4f " %(((ndimage.minimum(cloudElement, labels=labels))/float((ndimage.maximum(cloudElement, labels=labels))))*100.0))
    				cloudElementsFile.write("\nEccentricity is: %.4f " %(cloudElementEpsilon))
    				cloudElementsFile.write("\n-----------------------------------------------")
    				
			#reset list for the next CE
			nodeExist = False
			cloudElementCenter=[]
			cloudElement = []
			cloudElementCenter = []
			cloudElementLat=[]
			cloudElementLon =[]
			cloudElementLatLons =[]
			brightnesstemp1 =[]
			brightnesstemp =[]
			finalCETRMMvalues =[]
			CEprecipRate =[]
			CETRMMList =[]
			precipTotal = 0.0
			precip=[]
			TRMMCloudElementLatLons=[]
			
		#reset for the next time
		prevFrameCEs =[]
		prevFrameCEs = currFrameCEs
		currFrameCEs =[]
		    			
	cloudElementsFile.close
	cloudElementsUserFile.close
	#if using ARCGIS data store code, uncomment this file close line
	#cloudElementsTextFile.close

	#clean up graph - remove parent and childless nodes
	outAndInDeg = CLOUD_ELEMENT_GRAPH.degree_iter()
	toRemove = [node[0] for node in outAndInDeg if node[1]<1]
	CLOUD_ELEMENT_GRAPH.remove_nodes_from(toRemove)
	
	print "number of nodes are: ", CLOUD_ELEMENT_GRAPH.number_of_nodes()
	print "number of edges are: ", CLOUD_ELEMENT_GRAPH.number_of_edges()
	print ("*"*80)

	#hierachial graph output
	#graphTitle = "Cloud Elements observed over Niamey, Niger 11 Sep 2006 00Z - 12 Sep 2006 12Z"
	graphTitle = "Cloud Elements observed over Burkina Faso 31 Aug 2009 00Z - 01 Sep 2008 23Z" # Niamey, Niger"
	drawGraph(CLOUD_ELEMENT_GRAPH, graphTitle, edgeWeight)

	return CLOUD_ELEMENT_GRAPH	
#******************************************************************
def findPrecipRate(TRMMdirName):
	'''
	TODO: needs fixing 
	Purpose:: Determines the precipitation rates for MCSs found if TRMMdirName was not entered in findCloudElements this can be used

	Input:: TRMMdirName: a string representing the directory for the original TRMM netCDF files

    Output:: a list of dictionary of the TRMM data 
    	NB: also creates netCDF with TRMM data for each CE (for post processing) index
    		in MAINDIRECTORY/TRMMnetcdfCEs
   
    Assumptions:: Assumes that findCloudElements was run without the TRMMdirName value 
 
	'''
	allCEnodesTRMMdata =[]
	TRMMdataDict={}
	precipTotal = 0.0

	os.chdir((MAINDIRECTORY+'/MERGnetcdfCEs/'))
	imgFilename = ''
	temporalRes = 3 #3 hours for TRMM
	
	#sort files
	files = filter(os.path.isfile, glob.glob("*.nc"))
	files.sort(key=lambda x: os.path.getmtime(x))
	
	for afile in files:
		#try:
		print "in for ", afile
		fullFname = os.path.splitext(afile)[0]
		noFrameExtension = (fullFname.replace("_","")).split('F')[0]
		CEuniqueID = 'F' +(fullFname.replace("_","")).split('F')[1]
		fileDateTimeChar = (noFrameExtension.replace(":","")).split('s')[1]
		fileDateTime = fileDateTimeChar.replace("-","")
		fileDate = fileDateTime[:-6]
		fileHr=fileDateTime[-6:-4]

		cloudElementData = Dataset(afile,'r', format='NETCDF4')
		brightnesstemp = cloudElementData.variables['brightnesstemp'][:]
		latsrawCloudElements = cloudElementData.variables['latitude'][:]
		lonsrawCloudElements = cloudElementData.variables['longitude'][:]
			
		
		if int(fileHr) % 3 == 0:
			TRMMfileName = TRMMdirName+'/3B42.'+ fileDate + "."+fileHr+".7A.nc"
			#print "TRMMfileName is ", TRMMfileName
			TRMMData = Dataset(TRMMfileName,'r', format='NETCDF4')
			precipRate = TRMMData.variables['pcp'][:,:,:]
			latsrawTRMMData = TRMMData.variables['latitude'][:]
			lonsrawTRMMData = TRMMData.variables['longitude'][:]
			lonsrawTRMMData[lonsrawTRMMData > 180] = lonsrawTRMMData[lonsrawTRMMData>180] - 360.
			LONTRMM, LATTRMM = np.meshgrid(lonsrawTRMMData, latsrawTRMMData)

			#nygrdTRMM = len(LATTRMM[:,0]); nxgrd = len(LONTRMM[0,:])
			nygrd = len(LAT[:, 0]); nxgrd = len(LON[0, :])

			precipRateMasked = ma.masked_array(precipRate, mask=(precipRate < 0.0))
			#---------regrid the TRMM data to the MERG dataset ----------------------------------
			#regrid using the do_regrid stuff from the Apache OCW 
			regriddedTRMM = ma.zeros((0, nygrd, nxgrd))
			regriddedTRMM = process.do_regrid(precipRateMasked[0,:,:], LATTRMM,  LONTRMM, LAT, LON, order=1, mdi= -999999999)
			#----------------------------------------------------------------------------------

			# #get the lat/lon info from cloudElement
			latCEStart = LAT[0][0]
			latCEEnd = LAT[-1][0]
			lonCEStart = LON[0][0]
			lonCEEnd = LON[0][-1]

			#get the lat/lon info for TRMM data (different resolution)
			latStartT = find_nearest(latsrawTRMMData, latCEStart)
			latEndT = find_nearest(latsrawTRMMData, latCEEnd)
			lonStartT = find_nearest(lonsrawTRMMData, lonCEStart)
			lonEndT = find_nearest(lonsrawTRMMData, lonCEEnd)
			latStartIndex = np.where(latsrawTRMMData == latStartT)
			latEndIndex = np.where(latsrawTRMMData == latEndT)
			lonStartIndex = np.where(lonsrawTRMMData == lonStartT)
			lonEndIndex = np.where(lonsrawTRMMData == lonEndT)

			#get the relevant TRMM info 
			CEprecipRate = precipRate[:,(latStartIndex[0][0]-1):latEndIndex[0][0],(lonStartIndex[0][0]-1):lonEndIndex[0][0]]
			TRMMData.close()
				

			
			# ------ NETCDF File stuff ------------------------------------
			thisFileName = MAINDIRECTORY+'/TRMMnetcdfCEs/'+ fileDateTime + CEuniqueID +'.nc'
			# print "thisFileName ", thisFileName
			# sys.exit()
			currNetCDFData = Dataset(thisFileName, 'w', format='NETCDF4')
			currNetCDFData.description = 'Cloud Element '+CEuniqueID + ' rainfall data'
			currNetCDFData.calendar = 'standard'
			currNetCDFData.conventions = 'COARDS'
			# dimensions
			currNetCDFData.createDimension('time', None)
			currNetCDFData.createDimension('lat', CEprecipRate.shape[1])
			currNetCDFData.createDimension('lon', CEprecipRate.shape[2])
			# variables
			TRMMprecip = ('time','lat', 'lon',)
			times = currNetCDFTRMMData.createVariable('time', 'f8', ('time',))
			times.units = 'hours since '+ str(timelist[t])[:-6]
			latitude = currNetCDFTRMMData.createVariable('latitude', 'f8', ('lat',))
			longitude = currNetCDFTRMMData.createVariable('longitude', 'f8', ('lon',))
			rainFallacc = currNetCDFTRMMData.createVariable('precipitation_Accumulation', 'f8',TRMMprecip )
			rainFallacc.units = 'mm'

			longitude[:] = LON[0,:]
			longitude.units = "degrees_east" 
			longitude.long_name = "Longitude" 

			latitude[:] =  LAT[:,0]
			latitude.units = "degrees_north"
			latitude.long_name ="Latitude"

			finalCETRMMvalues = ma.zeros((brightnesstemp.shape))
			#-----------End most of NETCDF file stuff ------------------------------------	
			#finalCETRMMvalues = ma.zeros((CEprecipRate.shape))
			for index,value in np.ndenumerate(brightnesstemp):
				#print "index, value ", index, value
				time_index, lat_index, lon_index = index
				currTimeValue = 0
				if value > 0:
					finalCETRMMvalues[0,int(np.where(LAT[:,0]==brightnesstemp[time_index,lat_index])[0]),int(np.where(LON[0,:]==brightnesstemp[time_index,lon_index])[0])] = regriddedTRMM[int(np.where(LAT[:,0]==brightnesstemp[time_index,lat_index])[0]),int(np.where(LON[0,:]==brightnesstemp[time_index,lon_index])[0])]
						

					# #print "lat_index and value ", lat_index, latsrawCloudElements[lat_index]
					# currLatvalue = find_nearest(latsrawTRMMData, latsrawCloudElements[lat_index])
					# currLonValue = find_nearest(lonsrawTRMMData ,lonsrawCloudElements[lon_index])
					# currLatIndex = np.where(latsrawTRMMData==currLatvalue)[0][0]-latStartIndex[0][0]
					# currLonIndex = np.where(lonsrawTRMMData==currLonValue)[0][0]- lonStartIndex[0][0]
					# #print "currLatIndex , currLonIndex ", currLatIndex , currLonIndex
					# finalCETRMMvalues[time_index,currLatIndex , currLonIndex] = value * TRES*1.0 #because the rainfall TRMM is mm/hr
					# # if currLatvalue != prevLatValue and currLonValue != prevLonValue:
					# # 	precipTotal = value*temporalRes*1.0
					# # prevLatValue = currLatvalue
					# # prevLonValue = currLonValue

			TRMMnumOfBoxes = np.count_nonzero(finalCETRMMvalues)
			TRMMArea = TRMMnumOfBoxes*XRES*YRES		
			rainFallacc[:] = finalCETRMMvalues
			currNetCDFData.close()
			for index, value in np.ndenumerate(finalCETRMMvalues):
					#print "index, value ", index, value
					precipTotal += value 

			# #add info to the dictionary and to the list
			# TRMMdataDict = {'uniqueID': CEuniqueID, 'cloudElementTime': (fullFname.replace("_"," ").split('F')[0]).split('s')[1],'cloudElementLatLon': finalCETRMMvalues, 'cloudElementPrecipTotal':precipTotal}
			# allCEnodesTRMMdata.append(TRMMdataDict)
			# print "precipTotal is ", precipTotal
			#add info to CLOUDELEMENTSGRAPH
			for eachdict in CLOUD_ELEMENT_GRAPH.nodes(CEuniqueID):
				if eachdict[1]['uniqueID'] == CEuniqueID:
					if not 'cloudElementPrecipTotal' in eachdict[1].keys():
						eachdict[1]['cloudElementPrecipTotal'] = precipTotal
					if not 'cloudElementLatLonTRMM' in eachdict[1].keys():
						eachdict[1]['cloudElementLatLonTRMM'] = finalCETRMMvalues
					if not 'TRMMArea' in eachdict[1].keys():
						eachdict[1]['TRMMArea'] = TRMMArea
		#clean up
		precipTotal = 0.0
		latsrawTRMMData =[]
		lonsrawTRMMData = []
		latsrawCloudElements=[]
		lonsrawCloudElements=[]
		finalCETRMMvalues =[]
		CEprecipRate =[]
		brightnesstemp =[]
		TRMMdataDict ={}

	return allCEnodesTRMMdata
#******************************************************************	
def findCloudClusters(CEGraph):
	'''
	Purpose:: Determines the cloud clusters properties from the subgraphs in 
	    the graph i.e. prunes the graph according to the minimum depth

	Input:: CEGraph: 1 graph -  a directed graph of the CEs with weighted edges
			    according the area overlap between nodes (CEs) of consectuive frames
    
    Output:: PRUNED_GRAPH: 1 graph - a directed graph of with CCs/ MCSs

	'''

	seenNode = []
	allMCSLists =[]
	pathDictList =[]
	pathList=[]

	cloudClustersFile = open((MAINDIRECTORY+'/textFiles/cloudClusters.txt'),'wb')
	
	for eachNode in CEGraph:
		#check if the node has been seen before
		if eachNode not in dict(enumerate(zip(*seenNode))):
			#look for all trees associated with node as the root
			thisPathDistanceAndLength = nx.single_source_dijkstra(CEGraph, eachNode)
			#determine the actual shortestPath and minimum depth/length
			maxDepthAndMinPath = findMaxDepthAndMinPath(thisPathDistanceAndLength)
			if maxDepthAndMinPath:
				maxPathLength = maxDepthAndMinPath[0] 
				shortestPath = maxDepthAndMinPath[1]
				
				#add nodes and paths to PRUNED_GRAPH
				for i in xrange(len(shortestPath)):
					if PRUNED_GRAPH.has_node(shortestPath[i]) is False:
						PRUNED_GRAPH.add_node(shortestPath[i])
						
					#add edge if necessary
					if i < (len(shortestPath)-1) and PRUNED_GRAPH.has_edge(shortestPath[i], shortestPath[i+1]) is False:
						prunedGraphEdgeweight = CEGraph.get_edge_data(shortestPath[i], shortestPath[i+1])['weight']
						PRUNED_GRAPH.add_edge(shortestPath[i], shortestPath[i+1], weight=prunedGraphEdgeweight)

				#note information in a file for consideration later i.e. checking to see if it works
				cloudClustersFile.write("\nSubtree pathlength is %d and path is %s" %(maxPathLength, shortestPath))
				#update seenNode info
				seenNode.append(shortestPath)	

	print "pruned graph"
	print "number of nodes are: ", PRUNED_GRAPH.number_of_nodes()
	print "number of edges are: ", PRUNED_GRAPH.number_of_edges()
	print ("*"*80)		
					
	#graphTitle = "Cloud Clusters observed over Niamey, Niger 11 Sep 2006 00Z - 12 Sep 2006 12Z"
	graphTitle = "Cloud Clusters observed over  Burkina Faso 31 Aug 2009 00Z - 01 Sep 2008 23Z"
	drawGraph(PRUNED_GRAPH, graphTitle, edgeWeight)
	cloudClustersFile.close
	
	return PRUNED_GRAPH  
#******************************************************************
def findMCC (prunedGraph):
	'''
	Purpose:: Determines if subtree is a MCC according to Laurent et al 1998 criteria

	Input:: prunedGraph: a Networkx Graph representing the CCs 

    Output:: finalMCCList: a list of list of tuples representing a MCC
             
    Assumptions: frames are ordered and are equally distributed in time e.g. hrly satellite images
 
	'''
	MCCList = []
	MCSList = []
	definiteMCC = []
	definiteMCS = []
	eachList =[]
	eachMCCList =[]
	maturing = False
	decaying = False
	fNode = ''
	lNode = ''
	removeList =[]
	imgCount = 0
	imgTitle =''
	
	maxShieldNode = ''
	orderedPath =[]
	treeTraversalList =[]
	definiteMCCFlag = False
	unDirGraph = nx.Graph()
	aSubGraph = nx.DiGraph()
	definiteMCSFlag = False

	
	#connected_components is not available for DiGraph, so generate graph as undirected 
	unDirGraph = PRUNED_GRAPH.to_undirected()
	subGraph = nx.connected_component_subgraphs(unDirGraph)

	#for each path in the subgraphs determined
	for path in subGraph:
		#definite is a subTree provided the duration is longer than 3 hours

		if len(path.nodes()) > MIN_MCS_DURATION:
			orderedPath = path.nodes()
			orderedPath.sort(key=lambda item:(len(item.split('C')[0]), item.split('C')[0]))
			#definiteMCS.append(orderedPath)

			#build back DiGraph for checking purposes/paper purposes
			aSubGraph.add_nodes_from(path.nodes())	
			for eachNode in path.nodes():
				if prunedGraph.predecessors(eachNode):
					for node in prunedGraph.predecessors(eachNode):
						aSubGraph.add_edge(node,eachNode,weight=edgeWeight[0])

				if prunedGraph.successors(eachNode):
					for node in prunedGraph.successors(eachNode):
						aSubGraph.add_edge(eachNode,node,weight=edgeWeight[0])
			imgTitle = 'CC'+str(imgCount+1)
			drawGraph(aSubGraph, imgTitle, edgeWeight) #for eachNode in path:
			imgCount +=1
			#----------end build back ---------------------------------------------

			mergeList, splitList = hasMergesOrSplits(path)	
			#add node behavior regarding neutral, merge, split or both
			for node in path:
				if node in mergeList and node in splitList:
					addNodeBehaviorIdentifier(node,'B')
				elif node in mergeList and not node in splitList:
					addNodeBehaviorIdentifier(node,'M')
				elif node in splitList and not node in mergeList:
					addNodeBehaviorIdentifier(node,'S')
				else:
					addNodeBehaviorIdentifier(node,'N')
			

			#Do the first part of checking for the MCC feature
			#find the path
			treeTraversalList = traverseTree(aSubGraph, orderedPath[0],[],[])
			#print "treeTraversalList is ", treeTraversalList
			#check the nodes to determine if a MCC on just the area criteria (consecutive nodes meeting the area and temp requirements)
			MCCList = checkedNodesMCC(prunedGraph, treeTraversalList)
			for aDict in MCCList:
				for eachNode in aDict["fullMCSMCC"]:
					addNodeMCSIdentifier(eachNode[0],eachNode[1])
				
			#do check for if MCCs overlap
			if MCCList:
				if len(MCCList) > 1:
					for count in range(len(MCCList)): #for eachDict in MCCList:
						#if there are more than two lists
						if count >= 1:
							#and the first node in this list
							eachList = list(x[0] for x in MCCList[count]["possMCCList"])
							eachList.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
							if eachList:
								fNode = eachList[0]
								#get the lastNode in the previous possMCC list
								eachList = list(x[0] for x in MCCList[(count-1)]["possMCCList"])
								eachList.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
								if eachList:
									lNode = eachList[-1]
									if lNode in CLOUD_ELEMENT_GRAPH.predecessors(fNode):
										for aNode in CLOUD_ELEMENT_GRAPH.predecessors(fNode):
											if aNode in eachList and aNode == lNode:
												#if edge_data is equal or less than to the exisitng edge in the tree append one to the other
												if CLOUD_ELEMENT_GRAPH.get_edge_data(aNode,fNode)['weight'] <= CLOUD_ELEMENT_GRAPH.get_edge_data(lNode,fNode)['weight']:
													MCCList[count-1]["possMCCList"].extend(MCCList[count]["possMCCList"]) 
													MCCList[count-1]["fullMCSMCC"].extend(MCCList[count]["fullMCSMCC"])
													MCCList[count-1]["durationAandB"] +=  MCCList[count]["durationAandB"]
													MCCList[count-1]["CounterCriteriaA"] += MCCList[count]["CounterCriteriaA"]
													MCCList[count-1]["highestMCCnode"] = MCCList[count]["highestMCCnode"]
													MCCList[count-1]["frameNum"] = MCCList[count]["frameNum"] 
													removeList.append(count)
				#update the MCCList
				if removeList:
					for i in removeList:
						if (len(MCCList)-1) > i:
							del MCCList[i]
							removeList =[]
				
			#check if the nodes also meet the duration criteria and the shape crieria
			for eachDict in MCCList:
				#order the fullMCSMCC list, then run maximum extent and eccentricity criteria 
				if (eachDict["durationAandB"] * TRES) >= MINIMUM_DURATION and (eachDict["durationAandB"] * TRES) <= MAXIMUM_DURATION:
					eachList = list(x[0] for x in eachDict["fullMCSMCC"])
					eachList.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
					eachMCCList = list(x[0] for x in eachDict["possMCCList"])
					eachMCCList.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
					
					#update the nodemcsidentifer behavior
					#find the first element eachMCCList in eachList, and ensure everything ahead of it is indicated as 'I', 
					#find last element in eachMCCList in eachList and ensure everything after it is indicated as 'D'
					#ensure that everything between is listed as 'M'
					for eachNode in eachList[:(eachList.index(eachMCCList[0]))]: 
						addNodeMCSIdentifier(eachNode,'I')

					addNodeMCSIdentifier(eachMCCList[0],'M')

					for eachNode in eachList[(eachList.index(eachMCCList[-1])+1):]:
						addNodeMCSIdentifier(eachNode, 'D')

					#update definiteMCS list
					for eachNode in orderedPath[(orderedPath.index(eachMCCList[-1])+1):]:
						addNodeMCSIdentifier(eachNode, 'D')

					#run maximum extent and eccentricity criteria
					maxExtentNode, definiteMCCFlag = maxExtentAndEccentricity(eachList)
					#print "maxExtentNode, definiteMCCFlag ", maxExtentNode, definiteMCCFlag
					if definiteMCCFlag == True:
						definiteMCC.append(eachList)


			definiteMCS.append(orderedPath)
			
			#reset for next subGraph	
			aSubGraph.clear()
			orderedPath=[]
			MCCList =[]
			MCSList =[]
			definiteMCSFlag = False
		
	return definiteMCC, definiteMCS
#******************************************************************
def traverseTree(subGraph,node, queue, checkedNodes=None):
	'''
	Purpose:: To traverse a tree using a modified depth-first iterative deepening (DFID) search algorithm 

	Input:: subGraph: a Networkx DiGraph representing a CC
			lengthOfsubGraph: an integer representing the length of the subgraph
			node: a string representing the node currently being checked
			queue: a list of strings representing a list of nodes in a stack functionality 
					i.e. First-In-FirstOut (FIFO) for sorting the information from each visited node
			checkedNodes: a list of strings representing the list of the nodes in the traversal
    
    Output:: checkedNodes: a list of strings representing the list of the nodes in the traversal

    Assumptions: frames are ordered and are equally distributed in time e.g. hrly satellite images
 
	'''
	if len(checkedNodes) == len(subGraph):
		return checkedNodes

	if not checkedNodes:
		queue =[]
		checkedNodes.append(node)
		
	#check one level infront first...if something does exisit, stick it at the front of the stack
	upOneLevel = subGraph.predecessors(node)
	downOneLevel = subGraph.successors(node)
	for parent in upOneLevel:
		if parent not in checkedNodes and parent not in queue:
			for child in downOneLevel:
				if child not in checkedNodes and child not in queue:
					queue.insert(0,child)
					#downCheckFlag = True
			queue.insert(0,parent)	

	for child in downOneLevel:
		if child not in checkedNodes and child not in queue:
			if len(subGraph.predecessors(child)) > 1 or node in checkedNodes:
				queue.insert(0,child)
			else:
				queue.append(child)		
	
	#print "^^^^^stack ", stack
	for eachNode in queue:
		if eachNode not in checkedNodes:
			#print "if eachNode ", checkedNodes, eachNode, stack
			checkedNodes.append(eachNode)
			return traverseTree(subGraph, eachNode, queue, checkedNodes)
	
	return checkedNodes 
#******************************************************************
def checkedNodesMCC (prunedGraph, nodeList):
	'''
	Purpose :: Determine if this path is (or is part of) a MCC and provides 
	           preliminary information regarding the stages of the feature

	Input:: prunedGraph: a Networkx Graph representing all the cloud clusters 
			nodeList: list of strings (CE ID) from the traversal
		
	Output:: potentialMCCList: list of dictionaries representing all possible MCC within the path
			 dictionary = {"possMCCList":[(node,'I')], "fullMCSMCC":[(node,'I')], "CounterCriteriaA": CounterCriteriaA, "durationAandB": durationAandB}
	'''
	
	CounterCriteriaAFlag = False
	CounterCriteriaBFlag = False
	INITIATIONFLAG = False
	MATURITYFLAG = False
	DECAYFLAG = False
	thisdict = {} #will have the same items as the cloudElementDict 
	cloudElementArea = 0.0
	epsilon = 0.0
	frameNum =0
	oldNode =''
	potentialMCCList =[]
	durationAandB = 0
	CounterCriteriaA = 0
	CountercriteriaB = 0

	#check for if the list contains only one string/node
	if type(nodeList) is str:
		oldNode=nodeList
		nodeList =[]
		nodeList.append(oldNode)

	for node in nodeList:
		thisdict = thisDict(node)
		CounterCriteriaAFlag = False
		CounterCriteriaBFlag = False
		existingFrameFlag = False

		if thisdict['cloudElementArea'] >= OUTER_CLOUD_SHIELD_AREA:
			#print "OUTER_CLOUD_SHIELD_AREA met by: ", node, INITIATIONFLAG, MATURITYFLAG, DECAYFLAG
			CounterCriteriaAFlag = True
			INITIATIONFLAG = True
			MATURITYFLAG = False
			#check if criteriaB is meet
			cloudElementArea,criteriaB = checkCriteriaB(thisdict['cloudElementLatLon'])

			#if Criteria A and B have been met, then the MCC is initiated, i.e. store node as potentialMCC
	   		if cloudElementArea >= INNER_CLOUD_SHIELD_AREA:
	   			#print "INNER_CLOUD_SHIELD_AREA met by: ", node, INITIATIONFLAG, MATURITYFLAG, DECAYFLAG
	   			CounterCriteriaBFlag = True
	   			#append this information on to the dictionary
	   			addInfothisDict(node, cloudElementArea, criteriaB)
	   			INITIATIONFLAG = False
	   			MATURITYFLAG = True
	   			stage = 'M'
	   			potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag) 			
   			else:
   				#criteria B failed
   				CounterCriteriaBFlag = False
   				if INITIATIONFLAG == True:
   					stage = 'I'   					
   					potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag)

   				elif (INITIATIONFLAG == False and MATURITYFLAG == True) or DECAYFLAG==True:
   					DECAYFLAG = True
   					MATURITYFLAG = False
   					stage = 'D'
   					potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag)
   		else:
   			#criteria A failed
   			CounterCriteriaAFlag = False
   			CounterCriteriaBFlag = False
   			#print "!!OUTER_CLOUD_SHIELD_AREA NOT met by: ", node, INITIATIONFLAG, MATURITYFLAG, DECAYFLAG
			#add as a CE before or after the main feature
			if INITIATIONFLAG == True or (INITIATIONFLAG == False and MATURITYFLAG == True):
				stage ="I"
				potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag)
   			elif (INITIATIONFLAG == False and MATURITYFLAG == False) or DECAYFLAG == True:
   				stage = "D"
   				DECAYFLAG = True
   				potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag)
   			elif (INITIATIONFLAG == False and MATURITYFLAG == False and DECAYFLAG == False):
   				stage ="I"
   				potentialMCCList = updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag)

	return potentialMCCList
#******************************************************************
def updateMCCList(prunedGraph, potentialMCCList,node,stage, CounterCriteriaAFlag, CounterCriteriaBFlag):
	'''
	Purpose :: Utility function to determine if a path is (or is part of) a MCC and provides 
	           preliminary information regarding the stages of the feature

	Input:: prunedGraph: a Networkx Graph representing all the cloud clusters
			potentialMCCList: a list of dictionaries representing the possible MCCs within a path
			node: a string representing the cloud element currently being assessed
			CounterCriteriaAFlag: a boolean value indicating whether the node meets the MCC criteria A according to Laurent et al
			CounterCriteriaBFlag: a boolean value indicating whether the node meets the MCC criteria B according to Laurent et al
	
	Output:: potentialMCCList: list of dictionaries representing all possible MCC within the path
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
	if potentialMCCList==[]:
		#list empty
		stage = 'I'
		if CounterCriteriaAFlag == True and CounterCriteriaBFlag ==True:
			potentialMCCList.append({"possMCCList":[(node,stage)], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 1, "durationAandB": 1, "highestMCCnode":node, "frameNum":frameNum})	
		elif CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
			potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 1, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	
		elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
			potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 0, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	

	else:
		#list not empty
		predecessorsFlag, index = isThereALink(prunedGraph, 1,node,potentialMCCList,1)
		
		if predecessorsFlag == True:	

			for eachNode in potentialMCCList[index]["possMCCList"]:# MCCDict["possMCCList"]:
				if int((eachNode[0].split('CE')[0]).split('F')[1]) == frameNum :
					existingFrameFlag = True
					
			#this MUST come after the check for the existing frame
			if CounterCriteriaAFlag == True and CounterCriteriaBFlag ==True:
				stage = 'M'
				potentialMCCList[index]["possMCCList"].append((node,stage))
				potentialMCCList[index]["fullMCSMCC"].append((node,stage))

			
			if existingFrameFlag == False:
				if CounterCriteriaAFlag == True and CounterCriteriaBFlag ==True:
					stage ='M'
					potentialMCCList[index]["CounterCriteriaA"]+= 1
					potentialMCCList[index]["durationAandB"]+=1
					if frameNum > potentialMCCList[index]["frameNum"]:
						potentialMCCList[index]["frameNum"] = frameNum
						potentialMCCList[index]["highestMCCnode"] = node
					return potentialMCCList

				#if this frameNum doesn't exist and this frameNum is less than the MCC node max frame Num (including 0), then append to fullMCSMCC list
				if frameNum > potentialMCCList[index]["frameNum"] or potentialMCCList[index]["frameNum"]==0:
					stage = 'I'
					if CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
						potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 1, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	
						return potentialMCCList
					elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
						potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 0, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	
						return potentialMCCList

			#if predecessor and this frame number already exist in the MCC list, add the current node to the fullMCSMCC list
			if existingFrameFlag == True:
				if CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
					potentialMCCList[index]["fullMCSMCC"].append((node,stage))
					potentialMCCList[index]["CounterCriteriaA"] +=1
					return potentialMCCList
				if CounterCriteriaAFlag == False:
					potentialMCCList[index]["fullMCSMCC"].append((node,stage))	
					return potentialMCCList	
				
		if predecessorsFlag == False:
			successorsFlag, index = isThereALink(prunedGraph, 2,node,potentialMCCList,2)
			
			if successorsFlag == True:
				for eachNode in potentialMCCList[index]["possMCCList"]: #MCCDict["possMCCList"]:
					if int((eachNode[0].split('CE')[0]).split('F')[1]) == frameNum:
						existingFrameFlag = True
						
				if CounterCriteriaAFlag == True and CounterCriteriaBFlag == True:
					stage = 'M'
					potentialMCCList[index]["possMCCList"].append((node,stage))
					potentialMCCList[index]["fullMCSMCC"].append((node,stage))
					if frameNum > potentialMCCList[index]["frameNum"] or potentialMCCList[index]["frameNum"] == 0:
						potentialMCCList[index]["frameNum"] = frameNum
						potentialMCCList[index]["highestMCCnode"] = node
					return potentialMCCList
		
				
				if existingFrameFlag == False:
					if stage == 'M':
						stage = 'D'
					if CounterCriteriaAFlag == True and CounterCriteriaBFlag ==True:
						potentialMCCList[index]["CounterCriteriaA"]+= 1
						potentialMCCList[index]["durationAandB"]+=1
					elif CounterCriteriaAFlag == True:
						potentialMCCList[index]["CounterCriteriaA"] += 1
					elif CounterCriteriaAFlag == False:
						potentialMCCList[index]["fullMCSMCC"].append((node,stage))
						return potentialMCCList
						#if predecessor and this frame number already exist in the MCC list, add the current node to the fullMCSMCC list
				else:
					if CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
						potentialMCCList[index]["fullMCSMCC"].append((node,stage))
						potentialMCCList[index]["CounterCriteriaA"] +=1
						return potentialMCCList
					if CounterCriteriaAFlag == False:
						potentialMCCList[index]["fullMCSMCC"].append((node,stage))	
						return potentialMCCList			

		#if this node isn't connected to exisiting MCCs check if it is connected to exisiting MCSs ...
		if predecessorsFlag == False and successorsFlag == False:
			stage = 'I'
			predecessorsMCSFlag, index = isThereALink(prunedGraph, 1,node,potentialMCCList,2)
			if predecessorsMCSFlag == True:
				if CounterCriteriaAFlag == True and CounterCriteriaBFlag == True:
					potentialMCCList[index]["possMCCList"].append((node,'M'))
					potentialMCCList[index]["fullMCSMCC"].append((node,'M'))
					potentialMCCList[index]["durationAandB"] += 1
					if frameNum > potentialMCCList[index]["frameNum"]:
						potentialMCCList[index]["frameNum"] = frameNum
						potentialMCCList[index]["highestMCCnode"] = node
					return potentialMCCList

				if potentialMCCList[index]["frameNum"] == 0 or frameNum <= potentialMCCList[index]["frameNum"]:
					if CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
						potentialMCCList[index]["fullMCSMCC"].append((node,stage))
						potentialMCCList[index]["CounterCriteriaA"] +=1
						return potentialMCCList
					elif CounterCriteriaAFlag == False:
						potentialMCCList[index]["fullMCSMCC"].append((node,stage))
						return potentialMCCList
			else:
				successorsMCSFlag, index = isThereALink(prunedGraph, 2,node,potentialMCCList,2)
				if successorsMCSFlag == True:
					if CounterCriteriaAFlag == True and CounterCriteriaBFlag == True:
						potentialMCCList[index]["possMCCList"].append((node,'M'))
						potentialMCCList[index]["fullMCSMCC"].append((node,'M'))
						potentialMCCList[index]["durationAandB"] += 1
						if frameNum > potentialMCCList[index]["frameNum"]:
							potentialMCCList[index]["frameNum"] = frameNum
							potentialMCCList[index]["highestMCCnode"] = node
						return potentialMCCList

					
					if potentialMCCList[index]["frameNum"] == 0 or frameNum <= potentialMCCList[index]["frameNum"]:
						if CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
							potentialMCCList[index]["fullMCSMCC"].append((node,stage))
							potentialMCCList[index]["CounterCriteriaA"] +=1
							return potentialMCCList
						elif CounterCriteriaAFlag == False:
							potentialMCCList[index]["fullMCSMCC"].append((node,stage))
							return potentialMCCList
					
			#if this node isn't connected to existing MCCs or MCSs, create a new one ...
			if predecessorsFlag == False and predecessorsMCSFlag == False and successorsFlag == False and successorsMCSFlag == False:	
				if CounterCriteriaAFlag == True and CounterCriteriaBFlag ==True:
					potentialMCCList.append({"possMCCList":[(node,stage)], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 1, "durationAandB": 1, "highestMCCnode":node, "frameNum":frameNum})	
				elif CounterCriteriaAFlag == True and CounterCriteriaBFlag == False:
					potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 1, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	
				elif CounterCriteriaAFlag == False and CounterCriteriaBFlag == False:
					potentialMCCList.append({"possMCCList":[], "fullMCSMCC":[(node,stage)], "CounterCriteriaA": 0, "durationAandB": 0, "highestMCCnode":"", "frameNum":0})	

	return potentialMCCList
#******************************************************************
def isThereALink(prunedGraph, upOrDown,node,potentialMCCList,whichList):
	'''
	Purpose: Utility script for updateMCCList mostly because there is no Pythonic way to break out of nested loops
	
	Input:: prunedGraph:a Networkx Graph representing all the cloud clusters
			upOrDown: an integer representing 1- to do predecesor check and 2 - to do successor checkedNodesMCC
			node: a string representing the cloud element currently being assessed
			potentialMCCList: a list of dictionaries representing the possible MCCs within a path
			whichList: an integer representing which list ot check in the dictionary; 1- possMCCList, 2- fullMCSMCC
			
	Output:: thisFlag: a boolean representing whether the list passed has in the parent or child of the node
			 index: an integer representing the location in the potentialMCCList where thisFlag occurs

	'''
	thisFlag = False
	index = -1
	checkList =""
	if whichList == 1:
		checkList = "possMCCList"
	elif whichList ==2:
		checkList = "fullMCSMCC"

	#check parents
	if upOrDown == 1:
		for aNode in prunedGraph.predecessors(node):
			#reset the index counter for this node search through potentialMCCList
			index = -1
			for MCCDict in potentialMCCList:
				index += 1
				if aNode in list(x[0] for x in MCCDict[checkList]): #[0]:
					thisFlag = True
					#get out of looping so as to avoid the flag being written over when another node in the predecesor list is checked
					return thisFlag, index

	#check children
	if upOrDown == 2:
		for aNode in prunedGraph.successors(node):
			#reset the index counter for this node search through potentialMCCList
			index = -1
			for MCCDict in potentialMCCList:
				index += 1
				
				if aNode in list(x[0] for x in MCCDict[checkList]): #[0]:
					thisFlag = True
					return thisFlag, index

	return thisFlag, index
#******************************************************************
def maxExtentAndEccentricity(eachList):
	'''
	Purpose:: perform the final check for MCC based on maximum extent and eccentricity criteria

	Input:: eachList: a list of strings  representing the node of the possible MCCs within a path

	Output:: maxShieldNode: a string representing the node with the maximum maxShieldNode
	         definiteMCCFlag: a boolean indicating that the MCC has met all requirements
	'''
	maxShieldNode =''
	maxShieldArea = 0.0
	maxShieldEccentricity = 0.0
	definiteMCCFlag = False
	
	if eachList:
		for eachNode in eachList:
			if (thisDict(eachNode)['nodeMCSIdentifier'] == 'M' or thisDict(eachNode)['nodeMCSIdentifier'] == 'D') and thisDict(eachNode)['cloudElementArea'] > maxShieldArea:
				maxShieldNode = eachNode
				maxShieldArea = thisDict(eachNode)['cloudElementArea']
				
		maxShieldEccentricity = thisDict(maxShieldNode)['cloudElementEccentricity']
		if thisDict(maxShieldNode)['cloudElementEccentricity'] >= ECCENTRICITY_THRESHOLD_MIN and thisDict(maxShieldNode)['cloudElementEccentricity'] <= ECCENTRICITY_THRESHOLD_MAX :
			#criteria met
			definiteMCCFlag = True
			
	return maxShieldNode, definiteMCCFlag		
#******************************************************************
def findMaxDepthAndMinPath (thisPathDistanceAndLength):
	'''
	Purpose:: To determine the maximum depth and min path for the headnode

	Input:: tuple of dictionaries representing the shortest distance and paths for a node in the tree as returned by nx.single_source_dijkstra
			thisPathDistanceAndLength({distance}, {path})
			{distance} = nodeAsString, valueAsInt, {path} = nodeAsString, pathAsList

	Output:: tuple of the max pathLength and min pathDistance as a tuple (like what was input)
			minDistanceAndMaxPath = ({distance},{path}) 
	'''
	maxPathLength = 0
	minPath = 0

	#maxPathLength for the node in question
	maxPathLength = max(len (values) for values in thisPathDistanceAndLength[1].values())

	#if the duration is shorter then the min MCS length, then don't store!
	if maxPathLength < MIN_MCS_DURATION: #MINIMUM_DURATION :
		minDistanceAndMaxPath = ()

	#else find the min path and max depth
	else:
		#max path distance for the node in question  
		minPath = max(values for values in thisPathDistanceAndLength[0].values())
		
		#check to determine the shortest path from the longest paths returned
		for pathDistance, path in itertools.izip(thisPathDistanceAndLength[0].values(), thisPathDistanceAndLength[1].values()):
			pathLength = len(path)
			#if pathLength is the same as the maxPathLength, then look the pathDistance to determine if the min
			if pathLength == maxPathLength :
				if pathDistance <= minPath:
					minPath = pathLength
					#store details if absolute minPath and deepest... so need to search this stored info in tuple myTup = {dict1, dict2}
					minDistanceAndMaxPath = (pathDistance, path)
	return minDistanceAndMaxPath
#******************************************************************
def thisDict (thisNode):
	'''
	Purpose:: return dictionary from graph if node exist in tree

	Input:: String - thisNode

	Output :: Dictionary - eachdict[1] associated with thisNode from the Graph

	'''
	for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
		if eachdict[1]['uniqueID'] == thisNode:
			return eachdict[1]
#******************************************************************
def checkCriteriaB (thisCloudElementLatLon):
	'''
	Purpose:: Determine if criteria B is met for a CEGraph

	Input:: 2d array of (lat,lon) variable from the node dictionary being currently considered

	Output :: float - cloudElementArea, masked array of values meeting the criteria - criteriaB

	'''
	cloudElementCriteriaBLatLon=[]

	frame, CEcounter = ndimage.measurements.label(thisCloudElementLatLon, structure=STRUCTURING_ELEMENT)
	frameCEcounter=0
	#determine min and max values in lat and lon, then use this to generate teh array from LAT,LON meshgrid
	
	minLat = min(x[0] for x in thisCloudElementLatLon)
	maxLat = max(x[0]for x in thisCloudElementLatLon)
	minLon = min(x[1]for x in thisCloudElementLatLon)
	maxLon = max(x[1]for x in thisCloudElementLatLon)

	#print "minLat, maxLat, minLon, maxLon ", minLat, maxLat, minLon, maxLon
	minLatIndex = np.argmax(LAT[:,0] == minLat)
	maxLatIndex = np.argmax(LAT[:,0]== maxLat)
	minLonIndex = np.argmax(LON[0,:] == minLon)
	maxLonIndex = np.argmax(LON[0,:] == maxLon)

	#print "minLatIndex, maxLatIndex, minLonIndex, maxLonIndex ", minLatIndex, maxLatIndex, minLonIndex, maxLonIndex

	criteriaBframe = ma.zeros(((abs(maxLatIndex - minLatIndex)+1), (abs(maxLonIndex - minLonIndex)+1)))
	
	for x in thisCloudElementLatLon:
		#to store the values of the subset in the new array, remove the minLatIndex and minLonindex from the
		#index given in the original array to get the indices for the new array
		#criteriaBframe[(np.argmax(LAT[:,0] == x[0])),(np.argmax(LON[0,:] == x[1]))] = x[2]
		criteriaBframe[(np.argmax(LAT[:,0] == x[0]) - minLatIndex),(np.argmax(LON[0,:] == x[1]) - minLonIndex)] = x[2]

	#print criteriaBframe
	#keep only those values < TBB_MAX
	tempMask = ma.masked_array(criteriaBframe, mask=(criteriaBframe >= INNER_CLOUD_SHIELD_TEMPERATURE), fill_value = 0)
	
	#get the actual values that the mask returned
	criteriaB = ma.zeros((criteriaBframe.shape)).astype('int16')
	
	for index, value in maenumerate(tempMask): 
		lat_index, lon_index = index			
		criteriaB[lat_index, lon_index]=value	

   	for count in xrange(CEcounter):
   		#[0] is time dimension. Determine the actual values from the data
   		#loc is a masked array
   		#***** returns elements down then across thus (6,4) is 6 arrays deep of size 4
   		try:

	   		loc = ndimage.find_objects(criteriaB)[0]
	   	except:
	   		#this would mean that no objects were found meeting criteria B
	   		print "no objects at this temperature!"
	   		cloudElementArea = 0.0
	   		return cloudElementArea, cloudElementCriteriaBLatLon
	   
	   	print "after loc", loc
	   	print "************************"
	   	#print "criteriaB ", criteriaB.shape
	   	print criteriaB
	   	try:
	   		cloudElementCriteriaB = ma.zeros((criteriaB.shape))
	   		cloudElementCriteriaB =criteriaB[loc] 
	   	except:
	   		print "YIKESS"
	   		print "CEcounter ", CEcounter, criteriaB.shape
	   		print "criteriaB ", criteriaB

   		for index,value in np.ndenumerate(cloudElementCriteriaB):
   			if value !=0:
   				t,lat,lon = index
   				#add back on the minLatIndex and minLonIndex to find the true lat, lon values
   				lat_lon_tuple = (LAT[(lat),0], LON[0,(lon)],value)
   				cloudElementCriteriaBLatLon.append(lat_lon_tuple)

		cloudElementArea = np.count_nonzero(cloudElementCriteriaB)*XRES*YRES
		#do some
		tempMask =[]
		criteriaB =[]
		cloudElementCriteriaB=[]

		return cloudElementArea, cloudElementCriteriaBLatLon
#******************************************************************
def hasMergesOrSplits (nodeList):
	'''
	Purpose:: Determine if nodes within a path defined from shortest_path splittingNodeDict
	Input:: nodeList - list of nodes from a path
	Output:: two list_vars_in_file
			 splitList list of all the nodes in the path that split
			 mergeList list of all the nodes in the path that merged
	'''
	mergeList=[]
	splitList=[]

	for node,numParents in PRUNED_GRAPH.in_degree(nodeList).items():
		if numParents > 1:
			mergeList.append(node)

	for node, numChildren in PRUNED_GRAPH.out_degree(nodeList).items():
		if numChildren > 1:
			splitList.append(node)
	#sort
	splitList.sort(key=lambda item:(len(item.split('C')[0]), item.split('C')[0]))
	mergeList.sort(key=lambda item:(len(item.split('C')[0]), item.split('C')[0]))
			
	return mergeList,splitList
#******************************************************************
def allAncestors(path, aNode):
	'''
	Purpose:: Utility script to provide the path leading up to a nodeList

	Input:: list of strings - path: the nodes in the path 
	        string - aNode: a string representing a node to be checked for parents

	Output:: list of strings - path: the list of the nodes connected to aNode through its parents
			 integer - numOfChildren: the number of parents of the node passed
	'''

	numOfParents = PRUNED_GRAPH.in_degree(aNode)
	try:
		if PRUNED_GRAPH.predecessors(aNode) and numOfParents <= 1:
			path = path + PRUNED_GRAPH.predecessors(aNode)
			thisNode = PRUNED_GRAPH.predecessors(aNode)[0]
			return allAncestors(path,thisNode)
		else:
			path = path+aNode
			return path, numOfParents
	except:
		return path, numOfParents
#******************************************************************
def allDescendants(path, aNode):
	'''
	Purpose:: Utility script to provide the path leading up to a nodeList

	Input:: list of strings - path: the nodes in the path 
	        string - aNode: a string representing a node to be checked for children

	Output:: list of strings - path: the list of the nodes connected to aNode through its children
			 integer - numOfChildren: the number of children of the node passed
	'''

	numOfChildren = PRUNED_GRAPH.out_degree(aNode)
	try:
		if PRUNED_GRAPH.successors(aNode) and numOfChildren <= 1:
			path = path + PRUNED_GRAPH.successors(aNode)
			thisNode = PRUNED_GRAPH.successors(aNode)[0]
			return allDescendants(path,thisNode)
		else:
			path = path + aNode
			#i.e. PRUNED_GRAPH.predecessors(aNode) is empty
			return path, numOfChildren
	except:
		#i.e. PRUNED_GRAPH.predecessors(aNode) threw an exception
		return path, numOfChildren
#******************************************************************
def addInfothisDict (thisNode, cloudElementArea,criteriaB):
	'''
	Purpose:: update original dictionary node with information

	Input:: String - thisNode
			float - cloudElementArea, 
			masked array of floats meeting the criteria - criteriaB

	Output :: 

	'''
	for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
		if eachdict[1]['uniqueID'] == thisNode:
			eachdict[1]['CriteriaBArea'] = cloudElementArea
			eachdict[1]['CriteriaBLatLon'] = criteriaB
	return
#******************************************************************
def addNodeBehaviorIdentifier (thisNode, nodeBehaviorIdentifier):
	'''
	Purpose:: add an identifier to the node dictionary to indicate splitting, merging or neither node

	Input:: String - thisNode
	        String - nodeBehaviorIdentifier = S- split, M- merge, B- both split and merge, N- neither split or merge 

	Output :: None

	'''
	for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
		if eachdict[1]['uniqueID'] == thisNode:
			if not 'nodeBehaviorIdentifier' in eachdict[1].keys():
				eachdict[1]['nodeBehaviorIdentifier'] = nodeBehaviorIdentifier
	return
#******************************************************************
def addNodeMCSIdentifier (thisNode, nodeMCSIdentifier):
	'''
	Purpose:: add an identifier to the node dictionary to indicate splitting, merging or neither node

	Input:: String - thisNode
			String - nodeMCSIdentifier = 'I' for Initiation, 'M' for Maturity, 'D' for Decay
	       

	Output :: None

	'''
	for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
		if eachdict[1]['uniqueID'] == thisNode:
			if not 'nodeMCSIdentifier' in eachdict[1].keys():
				eachdict[1]['nodeMCSIdentifier'] = nodeMCSIdentifier
	return
#******************************************************************
def updateNodeMCSIdentifier (thisNode, nodeMCSIdentifier):
	'''
	Purpose:: update an identifier to the node dictionary to indicate splitting, merging or neither node

	Input:: String - thisNode
			String - nodeMCSIdentifier = 'I' for Initiation, 'M' for Maturity, 'D' for Decay
	       

	Output :: None

	'''
	for eachdict in CLOUD_ELEMENT_GRAPH.nodes(thisNode):
		if eachdict[1]['uniqueID'] == thisNode:
			eachdict[1]['nodeMCSIdentifier'] = nodeBehaviorIdentifier

	return
#******************************************************************
def eccentricity (cloudElementLatLon):
	'''
	Purpose::
	    Determines the eccentricity (shape) of contiguous boxes 
	    Values tending to 1 are more circular by definition, whereas 
	    values tending to 0 are more linear
	
	Input::
	    1 variable
		cloudElementLatLon: 3D array in (time,lat,lon),T_bb contiguous squares 
		
	Output::
	    1 variable
		epsilon: a float representing the eccentricity of the matrix passed
	
	'''
	
	epsilon = 0.0
	
	#loop over all lons and determine longest (non-zero) col
	#loop over all lats and determine longest (non-zero) row
	for latLon in cloudElementLatLon:
	    #assign a matrix to determine the legit values
	    
	    nonEmptyLons = sum(sum(cloudElementLatLon)>0)
        nonEmptyLats = sum(sum(cloudElementLatLon.transpose())>0)
        
        lonEigenvalues = 1.0 * nonEmptyLats / (nonEmptyLons+0.001) #for long oval on y axis
        latEigenvalues = 1.0 * nonEmptyLons / (nonEmptyLats +0.001) #for long oval on x-axs
        epsilon = min(latEigenvalues,lonEigenvalues)
        
	return epsilon
#******************************************************************
def cloudElementOverlap (currentCELatLons, previousCELatLons):
	'''
	Purpose::
	    Determines the percentage overlap between two list of lat-lons passed

	Input::
	    2 sorted list of tuples
	    currentCELatLons - the list of tuples for the current CE
	    previousCELatLons - the list of tuples for the other CE being considered

	Output::
	    2 variables 
	    percentageOverlap - a float representing the number of overlapping lat_lon tuples
	    areaOverlap - a floating-point number representing the area overlapping

	'''

	latlonprev =[]
	latloncurr = []
	count = 0 
	percentageOverlap = 0.0
	areaOverlap = 0.0

	#remove the temperature from the tuples for currentCELatLons and previousCELatLons then check for overlap
	latlonprev = [(x[0],x[1]) for x in previousCELatLons]
	latloncurr = [(x[0],x[1]) for x in currentCELatLons]  

	#find overlap
	count = len(list(set(latloncurr)&set(latlonprev)))

	#find area overlap
	areaOverlap = count*XRES*YRES
	
	#find percentage
	percentageOverlap = max(((count*1.0)/(len(latloncurr)*1.0)),((count*1.0)/(len(latlonprev)*1.0)))
	
	return percentageOverlap, areaOverlap
#******************************************************************
def findCESpeed(node, MCSList):
	'''
	Purpose:: to determine the speed of the CEs
			  uses vector displacement delta_lat/delta_lon (y/x)

	Input:: node: a string representing the CE
			MCSList: a list of strings representing the feature

	Output::

	'''

	delta_lon =0.0
	delta_lat =0.0
	CEspeed =[]
	theSpeed = 0.0
	

	theList = CLOUD_ELEMENT_GRAPH.successors(node)
	nodeLatLon=thisDict(node)['cloudElementCenter']
	#print "nodeLatLon ", nodeLatLon


	for aNode in theList:
		if aNode in MCSList:
			#if aNode is part of the MCSList then determine distance
			aNodeLatLon = thisDict(aNode)['cloudElementCenter']
			#print "aNodeLatLon ", aNodeLatLon
			#calculate CE speed
			#checking the lats
			nodeLatLon[0] += 90.0
			aNodeLatLon[0] += 90.0
			delta_lat = (nodeLatLon[0] - aNodeLatLon[0]) #convert to m
			#delta_lat = (nodeLatLon[0] - aNodeLatLon[0])*LAT_DISTANCE*1000 #convert to m
			#recall -ve ans --> northward tracking, -ve ans --> southwart tracking

			#checking lons lonsraw[lonsraw > 180] = lonsraw[lonsraw > 180] - 360.  # convert to -180,180 if necessary
			#recall +ve ans --> westward tracking, -ve ans --> eastward tracking
			# if nodeLatLon[1] < 0.0:
			# 	nodeLatLon[1] += 360.0
			# if aNodeLatLon[1] <= 0.0:
			# 	delta_lon = aNodeLatLon[1] + 360.0
			#0E --> 360 and E lons > west lons 
			nodeLatLon[1] += 360.0
			aNodeLatLon[1] += 360.0
			delta_lon = (nodeLatLon[1] - aNodeLatLon[1]) #convert to m
			#delta_lon = (nodeLatLon[1] - aNodeLatLon[1])*LON_DISTANCE*1000 #convert to m
			
			#print "delta_lat, delta_lon ", delta_lat, delta_lon

			#theSpeed = abs(((delta_lat*LAT_DISTANCE*1000)/(delta_lon*LON_DISTANCE*1000))/(TRES*3600)) #convert to s --> m/s
			theSpeed = abs((((delta_lat/delta_lon)*LAT_DISTANCE*1000)/(TRES*3600))) #convert to s --> m/s
			
			CEspeed.append(theSpeed)
			#print "aNode CE speed is ", aNode, (((delta_lat/delta_lon)*LAT_DISTANCE*1000)/(TRES*3600)), theSpeed

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
	    1 variable
		mArray - the masked array returned from the ma.array() command
		
		
	Output::
	    1 variable
		maskedValues - 3D (t,lat,lon), value of only masked values
	
	'''

	mask = ~mArray.mask.ravel()
	#beware yield fast, but generates a type called "generate" that does not allow for array methods
	for index, maskedValue in itertools.izip(np.ndenumerate(mArray), mask):
	    if maskedValue: 
			yield index	
#******************************************************************
def createMainDirectory(mainDirStr):
	'''
	Purpose:: to create the main directory for storing information and
			  the subdirectories for storing information
	Input:: mainDir: a directory for where all information generated from
			the program are to be stored
	Output:: None

	'''
	global MAINDIRECTORY

	MAINDIRECTORY = mainDirStr
	#if directory doesnt exist, creat it
	if not os.path.exists(MAINDIRECTORY):
		os.makedirs(MAINDIRECTORY)

	os.chdir((MAINDIRECTORY))
	#create the subdirectories
	try:	
		os.makedirs('images')
		os.makedirs('textFiles')
		os.makedirs('MERGnetcdfCEs')
		os.makedirs('TRMMnetcdfCEs')
	except:
		print "Directory exists already!!!"
		#TODO: some nice way of prompting if it is ok to continue...or just leave

	return 
#******************************************************************
def find_nearest(thisArray,value):
	'''
	Purpose :: to determine the value within an array closes to 
			another value

	Input ::
	Output::
	'''
	idx = (np.abs(thisArray-value)).argmin()
	return thisArray[idx]
#******************************************************************	
def preprocessingMERG(MERGdirname):
	'''
	Purpose::
	    Utility script for unzipping and converting the merg*.Z files from Mirador to 
	    NETCDF format. The files end up in a folder called mergNETCDF in the directory
	    where the raw MERG data is
	    NOTE: VERY RAW AND DIRTY 

	Input::
	    Directory to the location of the raw MERG files, preferably zipped
		
	Output::
	   none

	Assumptions::
	   1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
	     have been installed on the system and the user can access 
	   2 User can write files in location where script is being called
	   3 the files havent been unzipped	
	'''

	os.chdir((MERGdirname+'/'))
	imgFilename = ''

	#Just incase the X11 server is giving problems
	subprocess.call('export DISPLAY=:0.0', shell=True)

	for files in glob.glob("*-pixel"):
	#for files in glob.glob("*.Z"):
		fname = os.path.splitext(files)[0]

		#unzip it
		bash_cmd = 'gunzip ' + files
		subprocess.call(bash_cmd, shell=True)

		#determine the time from the filename
		ftime = re.search('\_(.*)\_',fname).group(1)

		yy = ftime[0:4]
		mm = ftime[4:6]
		day = ftime[6:8]
		hr = ftime [8:10]

		#TODO: must be something more efficient!

		if mm=='01':
			mth = 'Jan'
		if mm == '02':
			mth = 'Feb'
		if mm == '03':
			mth = 'Mar'
		if mm == '04':
			mth = 'Apr'
		if mm == '05':
			mth = 'May'
		if mm == '06':
			mth = 'Jun'
		if mm == '07':
			mth = 'Jul'
		if mm == '08':
			mth = 'Aug'
		if mm == '09':
			mth = 'Sep'
		if mm == '10':
			mth = 'Oct'
		if mm == '11':
			mth = 'Nov'
		if mm == '12':
			mth = 'Dec'


		subprocess.call('rm merg.ctl', shell=True)
		subprocess.call('touch merg.ctl', shell=True)
		replaceExpDset = 'echo DSET ' + fname +' >> merg.ctl'
		replaceExpTdef = 'echo TDEF 99999 LINEAR '+hr+'z'+day+mth+yy +' 30mn' +' >> merg.ctl'
		subprocess.call(replaceExpDset, shell=True) 
		subprocess.call('echo "OPTIONS yrev little_endian template" >> merg.ctl', shell=True)
		subprocess.call('echo "UNDEF  330" >> merg.ctl', shell=True)
		subprocess.call('echo "TITLE  globally merged IR data" >> merg.ctl', shell=True)
		subprocess.call('echo "XDEF 9896 LINEAR   0.0182 0.036378335" >> merg.ctl', shell=True)
		subprocess.call('echo "YDEF 3298 LINEAR   -59.982 0.036383683" >> merg.ctl', shell=True)
		subprocess.call('echo "ZDEF   01 LEVELS 1" >> merg.ctl', shell=True)
		subprocess.call(replaceExpTdef, shell=True)
		subprocess.call('echo "VARS 1" >> merg.ctl', shell=True)
		subprocess.call('echo "ch4  1  -1,40,1,-1 IR BT  (add  "75" to this value)" >> merg.ctl', shell=True)
		subprocess.call('echo "ENDVARS" >> merg.ctl', shell=True)

		#generate the lats4D command for GrADS
		lats4D = 'lats4d -v -q -lat '+LATMIN + ' ' +LATMAX +' -lon ' +LONMIN +' ' +LONMAX +' -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname
		
		#lats4D = 'lats4d -v -q -lat -40 -15 -lon 10 40 -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname
		#lats4D = 'lats4d -v -q -lat -5 40 -lon -90 60 -func @+75 ' + '-i merg.ctl' + ' -o ' + fname

		gradscmd = 'grads -blc ' + '\'' +lats4D + '\''
		#run grads and lats4d command
		subprocess.call(gradscmd, shell=True)
		imgFilename = hr+'Z'+day+mth+yy+'.gif'
		tempMaskedImages(imgFilename)

	#when all the files have benn converted, mv the netcdf files
	subprocess.call('mkdir mergNETCDF', shell=True)
	subprocess.call('mv *.nc mergNETCDF', shell=True)
	#mv all images
	subprocess.call('mkdir mergImgs', shell=True)
	subprocess.call('mv *.gif mergImgs', shell=True)
	return
#******************************************************************
def postProcessingNetCDF(dataset, dirName = None):
	'''
	
	TODO: UPDATE TO PICK UP LIMITS FROM FILE FOR THE GRADS SCRIPTS

	Purpose::
	    Utility script displaying the data in generated NETCDF4 files 
	    in GrADS
	    NOTE: VERY RAW AND DIRTY 

	Input::
	    dataset: integer representing post-processed MERG (1) or TRMM data (2) or original MERG(3)
	    string: Directory to the location of the raw (MERG) files, preferably zipped
		
	Output::
	   images in location as specfied in the code

	Assumptions::
	   1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
	     have been installed on the system and the user can access 
	   2 User can write files in location where script is being called	
	'''	
	
	coreDir = os.path.dirname(MAINDIRECTORY)
	#coreDir = os.path.dirname(os.path.abspath(__file__))
	ImgFilename = ''
	frameList=[]
	fileList =[]
	lines =[]
	var =''
	firstTime = True
	printLine = 0
	lineNum = 1
	#Just incase the X11 server is giving problems
	subprocess.call('export DISPLAY=:0.0', shell=True)

	print "coreDir is ", str(coreDir)
	prevFrameNum = 0

	if dataset == 1:
		var = 'ch4'
		dirName = MAINDIRECTORY+'/MERGnetcdfCEs'
		ctlTitle = 'TITLE MCC search Output Grid: Time  lat lon'
		ctlLine = 'brightnesstemp=\>ch4     1  t,y,x    brightnesstemperature'
		origsFile = coreDir+"/GrADSscripts/cs1.gs"
		gsFile = coreDir+"/GrADSscripts/cs2.gs"
		sologsFile = coreDir+"/GrADSscripts/mergeCE.gs"
		lineNum = 50
	
	elif dataset ==2:
		var = 'precipAcc'
		dirName = MAINDIRECTORY+'/TRMMnetcdfCEs'
		ctlTitle ='TITLE  TRMM MCS accumulated precipitation search Output Grid: Time  lat lon '
		ctlLine = 'precipitation_Accumulation=\>precipAcc     1  t,y,x    precipAccu'
		origsFile = coreDir+"/GrADSscripts/cs3.gs"
		gsFile = coreDir+"/GrADSscripts/cs4.gs"
		sologsFile = coreDir+"/GrADSscripts/TRMMCE.gs"
		lineNum = 10

	elif dataset ==3:
		var = 'ch4'
		ctlTitle = 'TITLE MERG DATA'
		ctlLine = 'ch4=\>ch4     1  t,y,x    brightnesstemperature'
		if dirName is None:
			print "Enter directory for original files"
			return
		else:
			origsFile = coreDir+"/GrADSscripts/cs1.gs"
			sologsFile = coreDir+"/GrADSscripts/infrared.gs"
			lineNum = 54			

	#sort files
	os.chdir((dirName+'/'))
	try:
		os.makedirs('ctlFiles')
	except:
		print "ctl file folder created already"
		
	files = filter(os.path.isfile, glob.glob("*.nc"))
	files.sort(key=lambda x: os.path.getmtime(x))
	for eachfile in files:
		fullFname = os.path.splitext(eachfile)[0]
		fnameNoExtension = fullFname.split('.nc')[0]
		if dataset == 1 or dataset == 2:
			frameNum = int((fnameNoExtension.split('CE')[0]).split('00F')[1])
		#create the ctlFile
		ctlFile1 = dirName+'/ctlFiles/'+fnameNoExtension + '.ctl'
		#the ctl file
		subprocessCall = 'rm ' +ctlFile1
		subprocess.call(subprocessCall, shell=True)
		subprocessCall = 'touch '+ctlFile1
		subprocess.call(subprocessCall, shell=True)
		lineToWrite = 'echo DSET ' + dirName+'/'+fnameNoExtension+'.nc' +' >>' + ctlFile1 
		subprocess.call(lineToWrite, shell=True)  
		lineToWrite = 'echo DTYPE netcdf >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo UNDEF 0 >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo '+ctlTitle+' >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo XDEF 413 LINEAR  -9.984375 0.036378335 >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo YDEF 412 LINEAR 5.03515625 0.036378335  >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo ZDEF   01 LEVELS 1 >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo TDEF 99999 linear 31aug2009 1hr >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo VARS 1 >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite ='echo '+ctlLine+' >> '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo ENDVARS >>  '+ctlFile1
		subprocess.call(lineToWrite, shell=True)
		lineToWrite = 'echo  >>  '+ctlFile1
		subprocess.call(lineToWrite, shell=True)

		#create plot of just that data
		subprocessCall = 'cp '+ origsFile+' '+sologsFile
		subprocess.call(subprocessCall, shell=True)

		ImgFilename = fnameNoExtension + '.gif'
					
		displayCmd = '\''+'d '+ var+'\''+'\n'
		newFileCmd = '\''+'open '+ ctlFile1+'\''+'\n'
		colorbarCmd = '\''+'run cbarn'+'\''+'\n'
		printimCmd = '\''+'printim '+MAINDIRECTORY+'/images/'+ImgFilename+' x800 y600 white\''+'\n'
		quitCmd = '\''+'quit'+'\''+'\n'
			
		GrADSscript = open(sologsFile,'r+')
		lines1 = GrADSscript.readlines()
		GrADSscript.seek(0)
		lines1.insert((1),newFileCmd)
		lines1.insert((lineNum+1),displayCmd)
		lines1.insert((lineNum+2), colorbarCmd)
		lines1.insert((lineNum+3), printimCmd)
		lines1.insert((lineNum + 4), quitCmd)
		GrADSscript.writelines(lines1)
		GrADSscript.close()
		#run the script
		runGrads = 'run '+ sologsFile
		gradscmd = 'grads -blc ' + '\'' +runGrads + '\''+'\n'
		subprocess.call(gradscmd, shell=True)

		if dataset == 1 or dataset == 2:

			if prevFrameNum != frameNum and firstTime == False:
				#counter for number of files (and for appending info to lines)
				count = 0
				subprocessCall = 'cp '+ origsFile+ ' '+gsFile
				subprocess.call(subprocessCall, shell=True)
				for fileName in frameList:
					if count == 0:
						frame1 = int((fileName.split('.nc')[0].split('CE')[0]).split('00F')[1])

					fnameNoExtension = fileName.split('.nc')[0]
					frameNum = int((fnameNoExtension.split('CE')[0]).split('00F')[1])
					
					if frameNum == frame1: 
						CE_num = fnameNoExtension.split('CE')[1]
						ImgFilename = fnameNoExtension.split('CE')[0] + '.gif'
						ctlFile1 = dirName+'/ctlFiles/'+fnameNoExtension + '.ctl'

						#build cs.gs script will all the CE ctl files and the appropriate display command
						newVar = var+'.'+CE_num
						newDisplayCmd = '\''+'d '+ newVar+'\''+'\n'
						newFileCmd = '\''+'open '+ ctlFile1+'\''+'\n'
						GrADSscript = open(gsFile,'r+')
						lines1 = GrADSscript.readlines()
						GrADSscript.seek(0)
						lines1.insert((1+count),newFileCmd)
						lines1.insert((lineNum+count+1),newDisplayCmd)
						GrADSscript.writelines(lines1)
						GrADSscript.close()
					count +=1

				colorbarCmd = '\''+'run cbarn'+'\''+'\n'
				printimCmd = '\''+'printim '+MAINDIRECTORY+'/images/'+ImgFilename+' x800 y600 white\''+'\n'
				quitCmd = '\''+'quit'+'\''+'\n'
				GrADSscript = open(gsFile,'r+')
				lines1 = GrADSscript.readlines()
				GrADSscript.seek(0)
				lines1.insert((lineNum+(count*2)+1), colorbarCmd)
				lines1.insert((lineNum + (count*2)+2), printimCmd)
				lines1.insert((lineNum + (count*2)+3), quitCmd)
				GrADSscript.writelines(lines1)
				GrADSscript.close()
				
				# if frameNum == 44:
				# 	sys.exit()
				

				#run the script
				runGrads = 'run '+ gsFile
				gradscmd = 'grads -blc ' + '\'' +runGrads + '\''+'\n'
				subprocess.call(gradscmd, shell=True)
				
				#remove the file data stuff
				subprocessCall = 'cd '+dirName
				
				#reset the list for the next frame
				fileList = frameList
				frameList = []
				for thisFile in fileList:
					if int(((thisFile.split('.nc')[0]).split('CE')[0]).split('00F')[1]) == frameNum:
						frameList.append(thisFile)
				frameList.append(eachfile)
				prevFrameNum = frameNum
				
			else:
				frameList.append(eachfile)
				prevFrameNum = frameNum
				firstTime = False
				
	return	
#******************************************************************	
def drawGraph (thisGraph, graphTitle, edgeWeight=None):
	'''
	Purpose:: Utility function to draw graph in the hierachial format

	Input:: a Networkx graph
			a string representing the graph title
			a list of integers representing the edge weights in the graph
	Output:: None
	'''
	
	imgFilename = MAINDIRECTORY+'/images/'+ graphTitle+".gif"
	fig=plt.figure(facecolor='white', figsize=(16,12)) #figsize=(10,8))#figsize=(16,12))
	
	edge95 = [(u,v) for (u,v,d) in thisGraph.edges(data=True) if d['weight'] == edgeWeight[0]]
	edge90 = [(u,v) for (u,v,d) in thisGraph.edges(data=True) if d['weight'] == edgeWeight[1]]
	edegeOverlap = [(u,v) for (u,v,d) in thisGraph.edges(data=True) if d['weight'] == edgeWeight[2]]

	nx.write_dot(thisGraph, 'test.dot')
	plt.title(graphTitle)
	pos = nx.graphviz_layout(thisGraph, prog='dot')
	#nx.draw(thisGraph, pos, with_labels=True, arrows=True)
	#draw graph in parts
	#nodes
	nx.draw_networkx_nodes(thisGraph, pos, with_labels=True, arrows=False)
	#edges
	nx.draw_networkx_edges(thisGraph, pos, edgelist=edge95, alpha=0.5, arrows=False) #with_labels=True, arrows=True)
	nx.draw_networkx_edges(thisGraph, pos, edgelist=edge90,  edge_color='b', style='dashed', arrows=False)
	nx.draw_networkx_edges(thisGraph, pos, edgelist=edegeOverlap, edge_color='y', style='dashed', arrows=False)
	#labels
	nx.draw_networkx_labels(thisGraph,pos, arrows=False) #,font_size=20,font_family='sans-serif')
	plt.axis('off')
	plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
	#do some clean up...and ensuring that we are in the right dir
	os.chdir((MAINDIRECTORY+'/'))
	subprocess.call('rm test.dot', shell=True)
	#plt.show()
#******************************************************************
def convert_timedelta(duration):
	'''
	Taken from http://stackoverflow.com/questions/14190045/how-to-convert-datetime-timedelta-to-minutes-hours-in-python

	'''

	days, seconds = duration.days, duration.seconds
	hours = days * 24 + seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = (seconds % 60)
	return hours, minutes, seconds
#******************************************************************
def tempMaskedImages(imgFilename):
	'''
	Purpose:: To generate temperature-masked images for a first pass verification

	Input::
	    filename for the gif file
		
	Output::
	    None - Gif images for each file of T_bb less than 250K are generated in folder called mergImgs

	Assumptions::
	   Same as for preprocessingMERG
	   1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
	     have been installed on the system and the user can access 
	   2 User can write files in location where script is being called
	   3 the files havent been unzipped	
	'''
	
	subprocess.call('rm tempMaskedImages.gs', shell=True)
	subprocess.call('touch tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'open merg.ctl''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'set mpdset hires''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'set lat -5 30''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'set lon -40 30''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'set cint 10''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'set clevs 190 200 210 220 230 240 250''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'d ch4+75''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'draw title Masked Temp @ '+imgFilename +'\'" >> tempMaskedImages.gs', shell=True)
	#printimCmd = 'printim '+imgFilename +' x1000 y800'
	subprocess.call('echo "''\'printim '+imgFilename +' x1000 y800''\'" >> tempMaskedImages.gs', shell=True)
	subprocess.call('echo "''\'quit''\'" >> tempMaskedImages.gs', shell=True)
	gradscmd = 'grads -blc ' + '\'run tempMaskedImages.gs''\'' 
	subprocess.call(gradscmd, shell=True)
	return
#******************************************************************
#******************************************************************
# 
#             METRICS FUNCTIONS FOR MERG.PY
#
#------------------------------------------------------------------
#1)Need to know the starttime and end time
#  - determine most common, least common and avg initiation time
#  - determine duration
#  
#2)Need criteria B area and temperature 
#  - determine max, min and avg area and T	
#  - visualization opportunity to show all the criteriaB for time
#	 on a map	
#
#3)Need temperature and area data
#  - calculate the max, min and average temp
#
#4)Need lat/lon and T for all MCC
#  - visualization of all MCCs during the time
#  - calculate speed of the system
# ****** Comparing with other datasets ******
#5)Need lat/lon and times for all MCCs
#  - use to locate same positions in dataset2 (e.g. TRMM) to 
#    determine precip
#******************************************************************
def numberOfFeatures(finalMCCList):
	'''
	Purpose:: To count the number of MCCs found for the period

	Input:: a list of list of strings - finalMCCList: a list of list of nodes representing a MCC
	
	Output::an integer representing the number of MCCs found

	Assumptions::

	'''
	return len(finalMCCList)
#******************************************************************
def temporalAndAreaInfoMetric(finalMCCList):
	'''
	Purpose:: To provide information regarding the temporal properties of the MCCs found

	Input:: List of dictionaries - finalMCCList: a list of dictionaries of nodes representing a MCC
	
	Output:: list of dictionaries - allMCCtimes {MCCtimes, starttime, endtime, duration, area): a list of dictionaries
			  of MCC temporal details for each MCC in the period considered

	Assumptions:: the final time hour --> the event lasted throughout that hr, therefore +1 to endtime
	'''
	#TODO: in real data edit this to use datetime
	#starttime =0
	#endtime =0
	#duration = 0
	MCCtimes =[]
	allMCCtimes=[]
	MCSArea =[]
	
	if finalMCCList:
		#print "len finalMCCList is: ", len(finalMCCList)
		for eachMCC in finalMCCList:
			#print "eachMCC count in temporalInfoMetric is ", len(eachMCC)
			#get the info from the node
			for eachNode in eachMCC:
				#print "eachNode in temporalInfoMetric is ", eachNode['uniqueID'], eachNode['cloudElementTime']
				MCCtimes.append(thisDict(eachNode)['cloudElementTime'])
				MCSArea.append(thisDict(eachNode)['cloudElementArea'])
			
			#sort and remove duplicates 
			MCCtimes=list(set(MCCtimes))
			MCCtimes.sort()
			#print "MCCtimes are: ", MCCtimes
			tdelta = MCCtimes[1] - MCCtimes[0]
			starttime = MCCtimes[0]
			endtime = MCCtimes[-1]
			duration = (endtime - starttime) + tdelta
			print "starttime ", starttime, "endtime ", endtime, "tdelta ", tdelta, "duration ", duration, "MCSAreas ", MCSArea
			allMCCtimes.append({'MCCtimes':MCCtimes, 'starttime':starttime, 'endtime':endtime, 'duration':duration, 'MCSArea': MCSArea})
			MCCtimes=[]
			MCSArea=[]
	else:
		allMCCtimes =[]
		tdelta = 0 # 00:00:00

	return allMCCtimes, tdelta
#******************************************************************
def longestDuration(allMCCtimes):
	'''
	Purpose:: To determine the longest MCC for the period

	Input:: list of dictionaries - allMCCtimes {MCCtimes, starttime, endtime, duration): a list of dictionaries
			  of MCC temporal details for each MCC in the period considered

	Output::an integer - lenMCC: representing the duration of the longest MCC found
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

	return sum([MCC['duration'] for MCC in allMCCtimes], timedelta(seconds=0))/len(allMCCtimes)
#******************************************************************
def averageTime (allTimes):
	'''
	Purpose:: To determine the average time in a list of datetimes 
			  e.g. of use is finding avg starttime, 
	Input:: allTimes: a list of datetimes representing all of a given event e.g. start time

	Output:: a float representing the average of the times given
	'''
	avgTime = 0

	for aTime in allTimes:
		avgTime += aTime.second + 60*aTime.minute + 3600*aTime.hour

	if len(allTimes) > 1:
		avgTime /= len(allTimes)
	
	rez = str(avgTime/3600) + ' ' + str((avgTime%3600)/60) + ' ' + str(avgTime%60)
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

	#for each node in the list, get the are information from the dictionary
	#in the graph and calculate the area
	for eachPath in finalMCCList:
		for eachNode in eachPath:
			thisMCC += thisDict(eachNode)['cloudElementArea']

		thisMCCAvg += (thisMCC/len(eachPath))
		thisMCC = 0.0

	#calcuate final average
	return thisMCCAvg/(len(finalMCCList))
#******************************************************************
def commonFeatureSize(finalMCCList): 
	'''
	Purpose:: To determine the common (mode) MCC size for the period

	Input:: a list of list of strings - finalMCCList: a list of list of nodes representing a MCC
	
	Output::a floating-point representing the average area of a MCC in the period
	        
	Assumptions:: 

	'''
	thisMCC = 0.0
	thisMCCAvg = []

	#for each node in the list, get the area information from the dictionary
	#in the graph and calculate the area
	for eachPath in finalMCCList:
		for eachNode in eachPath:
			thisMCC += eachNode['cloudElementArea']

		thisMCCAvg.append(thisMCC/len(eachPath))
		thisMCC = 0.0

	#calcuate 
	hist, bin_edges = np.histogram(thisMCCAvg)
	return hist,bin_edges
#******************************************************************
def commonFeatureDuration (finalMCCList):
	'''
	'''
#******************************************************************
def displaySize(finalMCCList): 
	'''
	Purpose:: To create a figure showing the area verse time for each MCS

	Input:: a list of list of strings - finalMCCList: a list of list of nodes representing a MCC
	
	Output:: None
	        
	Assumptions:: 

	'''
	timeList =[]
	count=1
	imgFilename=''
	minArea=10000.0
	maxArea=0.0
	eachNode={}

	#for each node in the list, get the area information from the dictionary
	#in the graph and calculate the area

	if finalMCCList:
		#print "len finalMCCList is: ", len(finalMCCList)
		for eachMCC in finalMCCList:
			#print "eachMCC count in temporalInfoMetric is ", len(eachMCC)
			#get the info from the node
			for node in eachMCC:
				eachNode=thisDict(node)
				timeList.append(eachNode['cloudElementTime'])

				if eachNode['cloudElementArea'] < minArea:
					minArea = eachNode['cloudElementArea']
				if eachNode['cloudElementArea'] > maxArea:
					maxArea = eachNode['cloudElementArea']

				
			#sort and remove duplicates 
			timeList=list(set(timeList))
			timeList.sort()
			tdelta = timeList[1] - timeList[0]
			starttime = timeList[0]-tdelta
			endtime = timeList[-1]+tdelta
			timeList.insert(0, starttime)
			timeList.append(endtime)

			#plot info
			plt.close('all')
			#title = 'Area verses time for MCS'+ str(count)
			title = 'Area distribution of the MCC over Burkina Faso'
			fig=plt.figure(facecolor='white', figsize=(18,10)) #figsize=(10,8))#figsize=(16,12))
			fig,ax = plt.subplots(1, facecolor='white', figsize=(10,10))
			
			#the data
			for node in eachMCC: #for eachNode in eachMCC:
				eachNode=thisDict(node)
				#ax.plot(eachNode['cloudElementTime'], eachNode['cloudElementArea'],'ro')
				if eachNode['cloudElementArea'] < 80000 : #2400.00:
					ax.plot(eachNode['cloudElementTime'], eachNode['cloudElementArea'],'bo', markersize=10)
					#eachNode['cloudElementArea'] >= 2400.00 and eachNode['cloudElementArea'] < 10000.00:
				elif eachNode['cloudElementArea'] >= 80000.00 and eachNode['cloudElementArea'] < 160000.00:
					ax.plot(eachNode['cloudElementTime'], eachNode['cloudElementArea'],'yo',markersize=20)
				else:
					ax.plot(eachNode['cloudElementTime'], eachNode['cloudElementArea'],'ro',markersize=30)
				
			#axes and labels
			maxArea += 1000.00
			ax.set_xlim(starttime,endtime)
			ax.set_ylim(minArea,maxArea)
			ax.set_ylabel('Area in km^2', fontsize=12)
			ax.set_title(title)
			ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d%H:%M:%S')
			fig.autofmt_xdate()
			
			plt.subplots_adjust(bottom=0.2)
			#plt.show()
			
			imgFilename = MAINDIRECTORY+'/images/'+ str(count)+'MCS.gif'
			plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
			
			#if time in not already in the time list, append it
			timeList=[]
			count += 1
	return 
#******************************************************************
def precipTotals(finalMCCList):
	'''
	Purpose:: Precipitation totals associated with a cloud element

	Input:: List of dictionaries - finalMCCList: a list of dictionaries of nodes representing a MCC

	Output:: precipTotal - to total amount of precipitation associated 
			with the feature
	'''
	precipTotal = 0.0
	CEprecip =0.0
	MCSPrecip=[]
	allMCSPrecip =[]
	count = 0

	if finalMCCList:
		#print "len finalMCCList is: ", len(finalMCCList)
		for eachMCC in finalMCCList:
			#get the info from the node
			for node in eachMCC:
				eachNode=thisDict(node)
				count += 1
				if count == 1:
					prevHr = int(str(eachNode['cloudElementTime']).replace(" ", "")[-8:-6])
				
				#print "prevHr ", prevHr
				currHr =int(str(eachNode['cloudElementTime']).replace(" ", "")[-8:-6])
				#print "currHr ", currHr
				print "time ",eachNode['cloudElementTime'], prevHr, currHr
				print "eachNode[cloudElementPrecipTotal]  ", eachNode['cloudElementPrecipTotal'] 
				if prevHr == currHr:
					CEprecip += eachNode['cloudElementPrecipTotal'] 
				else:
					MCSPrecip.append((prevHr,CEprecip))
					CEprecip = eachNode['cloudElementPrecipTotal'] 
				#last value in for loop
				if count == len(eachMCC):
					MCSPrecip.append((currHr, CEprecip))

				precipTotal += eachNode['cloudElementPrecipTotal'] 
				prevHr = currHr

			MCSPrecip.append(('0',precipTotal))
			print "MCSPrecip ", MCSPrecip

			allMCSPrecip.append(MCSPrecip)
			precipTotal =0.0
			CEprecip = 0.0
			MCSPrecip = []
			count = 0

		print "allMCSPrecip ", allMCSPrecip

	return allMCSPrecip
#******************************************************************
def precipMaxMin(finalMCCList):
	'''
	TODO: this doesnt work the np.min/max function seems to be not working with the nonzero option..possibly a problem upstream with cloudElementLatLonTRMM
	Purpose:: Precipitation maximum and min rates associated with each CE in MCS
	Input:: List of dictionaries - finalMCCList: a list of dictionaries of nodes representing a MCC

	Output:: a list tuples indicating max and min rate for each CE identified
	'''
	maxCEprecip = 0.0
	minCEprecip =0.0
	MCSPrecip=[]
	allMCSPrecip =[]


	if finalMCCList:
		if type(finalMCCList[0]) is str: # len(finalMCCList) == 1:
			for node in finalMCCList:
				eachNode = thisDict(node)
				CETRMM = eachNode['cloudElementLatLonTRMM']

				print "all ", np.min(CETRMM[np.nonzero(CETRMM)])
				print "minCEprecip ", np.min(eachNode['cloudElementLatLonTRMM']) #[np.nonzero(eachNode['cloudElementLatLonTRMM'])])

				print "maxCEprecip ", np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(eachNode['cloudElementLatLonTRMM'])])
				sys.exit()
				maxCEprecip = np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(eachNode['cloudElementLatLonTRMM'])])
				#np.max((eachNode['cloudElementLatLonTRMM'])[np.nonzero((eachNode['cloudElementLatLonTRMM']))])
				minCEprecip = np.min(eachNode['cloudElementLatLonTRMM'][np.nonzero(eachNode['cloudElementLatLonTRMM'])])
				#np.min((eachNode['cloudElementLatLonTRMM'])[np.nonzero((eachNode['cloudElementLatLonTRMM']))])
				MCSPrecip.append((eachNode['uniqueID'],minCEprecip, maxCEprecip))
			# for node in finalMCCList:
			# 	eachNode=thisDict(node) 
			# 	#find min and max precip
			# 	minCEprecip = min((eachNode['cloudElementLatLonTRMM'])[2])
			# 	maxCEprecip = max((eachNode['cloudElementLatLonTRMM'])[2])
			# 	MCSPrecip.append((eachNode['uniqueID'],minCEprecip, maxCEprecip))

		else:
			for eachMCC in finalMCCList:
				#get the info from the node
				for node in eachMCC: 
					eachNode=thisDict(node)
					#find min and max precip
					# minCEprecip = min((eachNode['cloudElementLatLonTRMM'])[2])
					# maxCEprecip = max((eachNode['cloudElementLatLonTRMM'])[2])
					# np.min(finalCETRMMvalues[np.nonzero(finalCETRMMvalues)])
					maxCEprecip =  np.max(eachNode['cloudElementLatLonTRMM'][np.nonzero(eachNode['cloudElementLatLonTRMM'])])
					#np.max((eachNode['cloudElementLatLonTRMM'])[np.nonzero((eachNode['cloudElementLatLonTRMM']))])
					minCEprecip =  np.min(eachNode['cloudElementLatLonTRMM'][np.nonzero(eachNode['cloudElementLatLonTRMM'])])
					#np.min((eachNode['cloudElementLatLonTRMM'])[np.nonzero((eachNode['cloudElementLatLonTRMM']))])
					MCSPrecip.append((eachNode['uniqueID'],minCEprecip, maxCEprecip))
				allMCSPrecip.append(MCSPrecip)
				MCSPrecip =[]
	 
	return MCSPrecip
#******************************************************************
def displayPrecip(finalMCCList): 
	'''
	Purpose:: To create a figure showing the precip rate verse time for each MCS

	Input:: a list of list of strings - finalMCCList: a list of list of nodes representing a MCC
	
	Output:: None
	        
	Assumptions:: 

	'''
	timeList =[]
	oriTimeList=[]
	colorBarTime =[]
	count=1
	imgFilename=''
	TRMMprecipDis =[]
	percentagePrecipitating = []#0.0
	CEArea=[]
	nodes=[]
	xy=[]
	x=[]
	y=[]
	precip = []
	partialArea =[]
	totalSize=0.0

	firstTime = True
	xStart =0.0
	yStart = 0.0

	num_bins = 5

	
	#for each node in the list, get the area information from the dictionary
	#in the graph and calculate the area

	if finalMCCList:
		#print "len finalMCCList is: ", len(finalMCCList)
		for eachMCC in finalMCCList:
			#get the info from the node
			for node in eachMCC:
				eachNode=thisDict(node)
				if firstTime == True:
					xStart = eachNode['cloudElementCenter'][1]#lon
					yStart = eachNode['cloudElementCenter'][0]#lat
				#print "eachNode in temporalInfoMetric is ", eachNode['uniqueID'], eachNode['cloudElementTime']
				timeList.append(eachNode['cloudElementTime'])
				percentagePrecipitating.append((eachNode['TRMMArea']/eachNode['cloudElementArea'])*100.0)
				#areaCenter.append((eachNode['cloudElementCenter'][1]-xStart, eachNode['cloudElementCenter'][0]-yStart))
				CEArea.append(eachNode['cloudElementArea'])
				nodes.append(eachNode['uniqueID'])
				x.append(eachNode['cloudElementCenter'][1])#-xStart)
				y.append(eachNode['cloudElementCenter'][0])#-yStart)
				
				firstTime= False

			#convert the timeList[] to list of floats
			for i in xrange(len(timeList)): #oriTimeList:
				colorBarTime.append(time.mktime(timeList[i].timetuple()))
			
			totalSize = sum(CEArea)
			partialArea = [(a/totalSize)*30000 for a in CEArea]
			
			#plot info
			plt.close('all')

			#title = 'Area verses time for MCS'+ str(count)
			title = 'Precipitation distribution of the MCS '
			#fig=plt.figure(facecolor='white', figsize=(10,10)) #figsize=(10,8))#figsize=(16,12))
			fig,ax = plt.subplots(1, facecolor='white', figsize=(20,7))

			cmap = cm.jet
			ax.scatter(x, y, s=partialArea,  c= colorBarTime, edgecolors='none', marker='o', cmap =cmap) #,vmin=colorBarTime[0],vmax=colorBarTime[-1]) 
			colorBarTime=[]
			colorBarTime =list(set(timeList))
			colorBarTime.sort()
			cb = colorbar_index(ncolors=len(colorBarTime), nlabels=colorBarTime, cmap = cmap)
			
			#axes and labels
			ax.set_xlabel('Degrees Longtude', fontsize=12)
			ax.set_ylabel('Degrees Latitude', fontsize=12)
			ax.set_title(title)
			ax.grid(True)
			plt.subplots_adjust(bottom=0.2)
			
			for i, txt in enumerate(nodes):
				if CEArea[i] >= 2400.00:
					ax.annotate('%d'%percentagePrecipitating[i]+'%', (x[i],y[i]))
				precip=[]

			imgFilename = MAINDIRECTORY+'/images/MCSprecip'+ str(count)+'.gif'
			plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
			
			#reset for next image
			timeList=[]
			percentagePrecipitating =[]
			CEArea =[]
			x=[]
			y=[]
			colorBarTime=[]
			nodes=[]
			precip=[]
			count += 1
			firstTime = True
	return 
#******************************************************************
def plotPrecipHistograms(finalMCCList):
	'''
	Purpose:: to create plots (histograms) of the each TRMMnetcdfCEs files

	Input:: finalMCCList: the list of strings representing the list of MCCs

	Output:: plots
	'''
	num_bins = 5
	precip =[]
	imgFilename = " "
	lastTime =" "
	firstTime = True
	MCScount = 0
	MSClen =0
	thisCount = 0
	totalPrecip=np.zeros((1,137,440))

	#TODO: use try except block instead
	if finalMCCList:

		for eachMCC in finalMCCList:
			firstTime = True
			MCScount +=1
			#totalPrecip=np.zeros((1,137,440))
			totalPrecip=np.zeros((1,413,412))

			#get the info from the node
			for node in eachMCC:
				eachNode=thisDict(node)
				thisTime = eachNode['cloudElementTime']
				MCSlen = len(eachMCC)
				thisCount += 1
				
				#this is the precipitation distribution plot from displayPrecip

				if eachNode['cloudElementArea'] >= 2400.0:
					if (str(thisTime) != lastTime and lastTime != " ") or thisCount == MCSlen:	
						plt.close('all')
						title = 'TRMM precipitation distribution for '+ str(thisTime)
						
						fig,ax = plt.subplots(1, facecolor='white', figsize=(7,5))
					
						n,binsdg = np.histogram(precip, num_bins)
						wid = binsdg[1:] - binsdg[:-1]
						plt.bar(binsdg[:-1], n/float(len(precip)), width=wid)

						#make percentage plot
						formatter = FuncFormatter(to_percent)
						plt.xlim(min(binsdg), max(binsdg))
						ax.set_xticks(binsdg)
						ax.set_xlabel('Precipitation [mm]', fontsize=12)
						ax.set_ylabel('Area', fontsize=12)
						ax.set_title(title)
						# Set the formatter
						plt.gca().yaxis.set_major_formatter(formatter)
						plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%0.0f'))
	    				imgFilename = MAINDIRECTORY+'/images/'+str(thisTime)+eachNode['uniqueID']+'TRMMMCS.gif'
	    				
	    				plt.savefig(imgFilename, transparent=True)
	    				#plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
	    				precip =[]
	    				
	    			# ------ NETCDF File get info ------------------------------------
					#thisFileName = '/Users/kimwhitehall/Documents/HU/research/mccsearch/TRMMnetcdf/TRMM' + str(thisTime).replace(" ", "_") + eachNode['uniqueID'] +'.nc'
					thisFileName = MAINDIRECTORY+'/TRMMnetcdfCEs/TRMM' + str(thisTime).replace(" ", "_") + eachNode['uniqueID'] +'.nc'
					TRMMData = Dataset(thisFileName,'r', format='NETCDF4')
					precipRate = TRMMData.variables['precipitation_Accumulation'][:,:,:]
					CEprecipRate = precipRate[0,:,:]
					TRMMData.close()
					if firstTime==True:
						totalPrecip=np.zeros((CEprecipRate.shape))
					
					totalPrecip = np.add(totalPrecip, precipRate)
					# ------ End NETCDF File ------------------------------------
					#if str(thisTime) == lastTime:
					for index, value in np.ndenumerate(CEprecipRate): 
						if value != 0.0:
							precip.append(value)

					#print "*******eachNode ", eachNode['uniqueID']
					lastTime = str(thisTime)
					firstTime = False
				else:
					lastTime = str(thisTime)
					firstTime = False  	
	return 
#******************************************************************
def plotHistogram(aList, aTitle, aLabel):
	'''
	Purpose:: to create plots (histograms) of the data entered in aList

	Input:: aList: the list of floating points representing values for e.g. averageArea, averageDuration, etc.
	        aTitle: a string representing the title and the name of the plot e.g. "Average area [km^2]"
	        aLabel: a string representing the x axis info i.e. the data that is being passed and the units e.g. "Area km^2"

	Output:: plots (gif files)
	'''
	num_bins = 10
	precip =[]
	imgFilename = " "
	lastTime =" "
	firstTime = True
	MCScount = 0
	MSClen =0
	thisCount = 0
	
	#TODO: use try except block instead
	if aList:
		
		fig,ax = plt.subplots(1, facecolor='white', figsize=(7,5))
	
		n,binsdg = np.histogram(aList, num_bins, density=True)
		wid = binsdg[1:] - binsdg[:-1]
		#plt.bar(binsdg[:-1], n/float(len(aList)), width=wid)
		plt.bar(binsdg[:-1], n, width=wid)
		# plt.hist(aList, num_bins, width=wid )


		#make percentage plot
		#formatter = FuncFormatter(to_percent)
		plt.xlim(min(binsdg), max(binsdg))
		ax.set_xticks(binsdg)#, rotation=45)
		ax.set_xlabel(aLabel, fontsize=12)
		#ax.set_ylabel('Frequency', fontsize=12)
		ax.set_title(aTitle)

		plt.xticks(rotation =45)
		# Set the formatter
		#plt.gca().yaxis.set_major_formatter(formatter)
		plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%0.0f'))
		plt.subplots_adjust(bottom=0.2)

		imgFilename = MAINDIRECTORY+'/images/'+aTitle.replace(" ","_")+'.gif'
		#plt.savefig(imgFilename, transparent=True)
		plt.savefig(imgFilename, facecolor=fig.get_facecolor(), transparent=True)
				
	return 
#******************************************************************
def plotAccTRMM (finalMCCList):
	'''
	Purpose:: (1) generate a file with the accumulated precipiation for the MCS
			 (2) generate the appropriate image
			TODO: NB: as the domain changes, will need to change XDEF and YDEF by hand to accomodate the new domain
			 TODO: look into getting the info from the NETCDF file

	Input:: finalMCCList: a list of strings representing the nodes that make a MCC (or MCS)
		    
	Output:: a netcdf file containing the accumulated precip 
			 a gif (generated in Grads)
	'''
	os.chdir((MAINDIRECTORY+'/TRMMnetcdfCEs'))
	fname =''
	imgFilename = ''
	firstPartName = ''
	firstTime = True
	
	#Just incase the X11 server is giving problems
	subprocess.call('export DISPLAY=:0.0', shell=True)

	#generate the file name using MCCTimes
	#if the file name exists, add it to the accTRMM file
	for path in finalMCCList:
		for eachNode in path:
			thisNode = thisDict(eachNode)
			fname = 'TRMM'+ str(thisNode['cloudElementTime']).replace(" ", "_") + thisNode['uniqueID'] +'.nc'
			
			if os.path.isfile(fname):	
				#open NetCDF file add info to the accu 
				print "opening TRMM file ", fname
				TRMMCEData = Dataset(fname,'r',format='NETCDF4')
				precipRate = TRMMCEData.variables['precipitation_Accumulation'][:]
				lats = TRMMCEData.variables['latitude'][:]
				lons = TRMMCEData.variables['longitude'][:]
				LONTRMM, LATTRMM = np.meshgrid(lons,lats)
				nygrdTRMM = len(LATTRMM[:,0]) 
				nxgrdTRMM = len(LONTRMM[0,:])
				precipRate = ma.masked_array(precipRate, mask=(precipRate < 0.0))
				TRMMCEData.close()

				if firstTime == True:
					firstPartName = str(thisNode['cloudElementTime']).replace(" ", "_")+'-'
					accuPrecipRate = ma.zeros((precipRate.shape))
					firstTime = False

				accuPrecipRate += precipRate

		imgFilename = MAINDIRECTORY+'/images/MCSaccu'+firstPartName+str(thisNode['cloudElementTime']).replace(" ", "_")+'.gif'
        #create new netCDF file
		accuTRMMFile = MAINDIRECTORY+'/TRMMnetcdfCEs/accu'+firstPartName+str(thisNode['cloudElementTime']).replace(" ", "_")+'.nc'
		#write the file
		accuTRMMData = Dataset(accuTRMMFile, 'w', format='NETCDF4')
		accuTRMMData.description =  'Accumulated precipitation data'
		accuTRMMData.calendar = 'standard'
		accuTRMMData.conventions = 'COARDS'
		# dimensions
		accuTRMMData.createDimension('time', None)
		accuTRMMData.createDimension('lat', nygrdTRMM)
		accuTRMMData.createDimension('lon', nxgrdTRMM)
		
		# variables
		TRMMprecip = ('time','lat', 'lon',)
		times = accuTRMMData.createVariable('time', 'f8', ('time',))
		times.units = 'hours since '+ str(thisNode['cloudElementTime']).replace(" ", "_")[:-6]
		latitude = accuTRMMData.createVariable('latitude', 'f8', ('lat',))
		longitude = accuTRMMData.createVariable('longitude', 'f8', ('lon',))
		rainFallacc = accuTRMMData.createVariable('precipitation_Accumulation', 'f8',TRMMprecip)
		rainFallacc.units = 'mm'

		longitude[:] = LONTRMM[0,:]
		longitude.units = "degrees_east" 
		longitude.long_name = "Longitude" 

		latitude[:] =  LATTRMM[:,0]
		latitude.units = "degrees_north"
		latitude.long_name ="Latitude"

		rainFallacc[:] = accuPrecipRate[:]

		accuTRMMData.close()

		#generate the image with GrADS
		#the ctl file
		subprocess.call('rm acc.ctl', shell=True)
		subprocess.call('touch acc.ctl', shell=True)
		replaceExpDset = 'echo DSET ' + accuTRMMFile +' >> acc.ctl'
		# replaceExpTdef = 'echo TDEF 99999 LINEAR 00Z 00000000 30mn' +' >> acc.ctl'
		subprocess.call(replaceExpDset, shell=True)  
		subprocess.call('echo "OPTIONS yrev little_endian template" >> acc.ctl', shell=True)
		subprocess.call('echo "DTYPE netcdf" >> acc.ctl', shell=True)
		subprocess.call('echo "UNDEF  0" >> acc.ctl', shell=True)
		subprocess.call('echo "TITLE  TRMM MCS accumulated precipitation" >> acc.ctl', shell=True)
		subprocess.call('echo "XDEF 413 LINEAR  -9.984375 0.036378335 " >> acc.ctl', shell=True)
        subprocess.call('echo "YDEF 412 LINEAR 5.03515625 0.036378335 " >> acc.ctl', shell=True)
        subprocess.call('echo "ZDEF   01 LEVELS 1" >> acc.ctl', shell=True)
        subprocess.call('echo "TDEF 99999 linear 31aug2009 1hr" >> acc.ctl', shell=True)
        #subprocess.call(replaceExpTdef, shell=True)
        subprocess.call('echo "VARS 1" >> acc.ctl', shell=True)
        subprocess.call('echo "precipitation_Accumulation=>precipAcc     1  t,y,x    precipAccu" >> acc.ctl', shell=True)
        subprocess.call('echo "ENDVARS" >> acc.ctl', shell=True)

        #generate GrADS script
        #print "thisNode ", thisNode
        #imgFilename = MAINDIRECTORY+'/images/MCSaccu'+firstPartName+str(thisNode['cloudElementTime']).replace(" ", "_")+'.gif'
        subprocess.call('rm accuTRMM1.gs', shell=True)
        subprocess.call('touch accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'reinit''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'open acc.ctl ''\'" >> accuTRMM1.gs', shell=True)
        #subprocess.call('echo "''\'open '+accuTRMMFile+ '\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'set grads off''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'set mpdset hires''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'set gxout shaded''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'set datawarn off''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'d precipacc''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'draw title TRMM Accumulated Precipitation [mm]''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'run cbarn''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'printim '+imgFilename +' x1000 y800 white''\'" >> accuTRMM1.gs', shell=True)
        subprocess.call('echo "''\'quit''\'" >> accuTRMM1.gs', shell=True)
        gradscmd = 'grads -blc ' + '\'run accuTRMM1.gs''\''
        subprocess.call(gradscmd, shell=True)

        #clean up
        subprocess.call('rm accuTRMM1.gs', shell=True)
        subprocess.call('rm acc.ctl', shell=True)
	
	return	
#******************************************************************
def plotAccuInTimeRange(starttime, endtime):
	'''
	Purpose:: create accumulated precip plot within a time range given using all CEs

	Input:: starttime: a string representing the time to start the accumulations format yyyy-mm-dd_hh:mm:ss
			endtime: a string representing the time to end the accumulations format yyyy-mm-dd_hh:mm:ss

	Output:: a netcdf file containing the accumulated precip for specified times
			 a gif (generated in Grads)

	TODO: pass of pick up from the NETCDF file the  lat, lon and resolution for generating the ctl file
	'''

	os.chdir((MAINDIRECTORY+'/TRMMnetcdfCEs/'))
	#Just incase the X11 server is giving problems
	subprocess.call('export DISPLAY=:0.0', shell=True)

	#fname =''
	imgFilename = ''
	firstPartName = ''
	firstTime = True

	fileList = []
	sTime = datetime.strptime(starttime.replace("_"," "),'%Y-%m-%d %H:%M:%S')
	eTime = datetime.strptime(endtime.replace("_"," "),'%Y-%m-%d %H:%M:%S')
	#tdelta = datetime.timedelta(0, 3600)
	thisTime = sTime

	while thisTime <= eTime:
		fileList = filter(os.path.isfile, glob.glob(('TRMM'+ str(thisTime).replace(" ", "_") + '*' +'.nc')))
		for fname in fileList:
			TRMMCEData = Dataset(fname,'r',format='NETCDF4')
			precipRate = TRMMCEData.variables['precipitation_Accumulation'][:]
			lats = TRMMCEData.variables['latitude'][:]
			lons = TRMMCEData.variables['longitude'][:]
			LONTRMM, LATTRMM = np.meshgrid(lons,lats)
			nygrdTRMM = len(LATTRMM[:,0]) 
			nxgrdTRMM = len(LONTRMM[0,:])
			precipRate = ma.masked_array(precipRate, mask=(precipRate < 0.0))
			TRMMCEData.close()

			if firstTime == True:
				accuPrecipRate = ma.zeros((precipRate.shape))
				firstTime = False

			accuPrecipRate += precipRate

		#increment the time
		thisTime +=timedelta(hours=TRES)

	#create new netCDF file
	accuTRMMFile = MAINDIRECTORY+'TRMMnetcdfCEs/accu'+starttime+'-'+endtime+'.nc'
	#write the file
	accuTRMMData = Dataset(accuTRMMFile, 'w', format='NETCDF4')
	accuTRMMData.description =  'Accumulated precipitation data'
	accuTRMMData.calendar = 'standard'
	accuTRMMData.conventions = 'COARDS'
	# dimensions
	accuTRMMData.createDimension('time', None)
	accuTRMMData.createDimension('lat', nygrdTRMM)
	accuTRMMData.createDimension('lon', nxgrdTRMM)
	
	# variables
	TRMMprecip = ('time','lat', 'lon',)
	times = accuTRMMData.createVariable('time', 'f8', ('time',))
	times.units = 'hours since '+ starttime[:-6]
	latitude = accuTRMMData.createVariable('latitude', 'f8', ('lat',))
	longitude = accuTRMMData.createVariable('longitude', 'f8', ('lon',))
	rainFallacc = accuTRMMData.createVariable('precipitation_Accumulation', 'f8',TRMMprecip)
	rainFallacc.units = 'mm'

	longitude[:] = LONTRMM[0,:]
	longitude.units = "degrees_east" 
	longitude.long_name = "Longitude" 

	latitude[:] =  LATTRMM[:,0]
	latitude.units = "degrees_north"
	latitude.long_name ="Latitude"

	rainFallacc[:] = accuPrecipRate[:]

	accuTRMMData.close()

	#generate the image with GrADS
	#the ctl file
	subprocess.call('rm acc.ctl', shell=True)
	subprocess.call('touch acc.ctl', shell=True)
	replaceExpDset = 'echo DSET ' + accuTRMMFile +' >> acc.ctl'
	subprocess.call(replaceExpDset, shell=True)  
	subprocess.call('echo "OPTIONS yrev little_endian template" >> acc.ctl', shell=True)
	subprocess.call('echo "DTYPE netcdf" >> acc.ctl', shell=True)
	subprocess.call('echo "UNDEF  0" >> acc.ctl', shell=True)
	subprocess.call('echo "TITLE  TRMM MCS accumulated precipitation" >> acc.ctl', shell=True)
	subprocess.call('echo "XDEF 413 LINEAR  -9.984375 0.036378335 " >> acc.ctl', shell=True)
	subprocess.call('echo "YDEF 412 LINEAR 5.03515625 0.036378335 " >> acc.ctl', shell=True)
	subprocess.call('echo "ZDEF   01 LEVELS 1" >> acc.ctl', shell=True)
	subprocess.call('echo "TDEF 99999 linear 31aug2009 1hr" >> acc.ctl', shell=True)
	subprocess.call('echo "VARS 1" >> acc.ctl', shell=True)
	subprocess.call('echo "precipitation_Accumulation=>precipAcc     1  t,y,x    precipAccu" >> acc.ctl', shell=True)
	subprocess.call('echo "ENDVARS" >> acc.ctl', shell=True)
	#generate GrADS script
	imgFilename = MAINDIRECTORY+'/images/accu'+starttime+'-'+endtime+'.gif'
	subprocess.call('rm accuTRMM1.gs', shell=True)
	subprocess.call('touch accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'reinit''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'open acc.ctl ''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'set grads off''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'set mpdset hires''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'set gxout shaded''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'set datawarn off''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'d precipacc''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'draw title TRMM Accumulated Precipitation [mm]''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'run cbarn''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'printim '+imgFilename +' x1000 y800 white''\'" >> accuTRMM1.gs', shell=True)
	subprocess.call('echo "''\'quit''\'" >> accuTRMM1.gs', shell=True)
	gradscmd = 'grads -blc ' + '\'run accuTRMM1.gs''\''
	subprocess.call(gradscmd, shell=True)

	#clean up
	subprocess.call('rm accuTRMM1.gs', shell=True)
	subprocess.call('rm acc.ctl', shell=True)

	return	
#******************************************************************
def createTextFile(finalMCCList, identifier):
	'''
	Purpose:: Create a text file with information about the MCS
			  This function is expected to be especially of use regarding 
			  long term record checks

	Input:: finalMCCList: list of list of strings representing list of MCSs nodes list
			identifier: an integer representing the type of list that has been entered...this is for creating file purposes
			1 - MCCList; 2- MCSList

	Output:: 
		     a user readable text file with all information about each MCS
		     a user readable text file with the summary of the MCS

	Assumptions:: 
	'''

	#allTimes =[]
	durations=0.0
	startTimes =[]
	endTimes=[]
	averagePropagationSpeed = 0.0
	speedCounter = 0
	maxArea =0.0
	amax = 0.0
	#avgMaxArea = 0.0
	avgMaxArea =[]
	maxAreaCounter =0.0
	maxAreaTime=''
	eccentricity = 0.0
	firstTime = True
	matureFlag = True
	timeMCSMatures=''
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
	allPropagationSpeeds =[]
	#averageAreas = 0.0
	averageAreas =[]
	areaAvg = 0.0
	avgPrecipTotal = 0.0
	avgPrecipTotalCounter = 0
	avgMaxMCSPrecipRate = 0.0
	avgMaxMCSPrecipRateCounter = 0
	avgMinMCSPrecipRate = 0.0
	avgMinMCSPrecipRateCounter = 0
	minMax =[]
	avgPrecipArea = []
	avgPrecipAreaPercent = 0.0
	precipArea = 0.0
	precipAreaPercent = 0.0
	precipPercent =[]
	precipCounter = 0
	precipAreaAvg = 0.0
	minSpeed = 0.0
	maxSpeed =0.0

	if identifier == 1:
		MCSUserFile = open((MAINDIRECTORY+'/textFiles/MCCsUserFile.txt'),'wb')
		MCSSummaryFile = open((MAINDIRECTORY+'/textFiles/MCCSummary.txt'),'wb')
	
	if identifier == 2:
		MCSUserFile = open((MAINDIRECTORY+'/textFiles/MCSsUserFile.txt'),'wb')
		MCSSummaryFile = open((MAINDIRECTORY+'/textFiles/MCSSummary.txt'),'wb')

	
	#MCCsFile = open((MAINDIRECTORY+'/textFiles/MCCsFile.txt'),'wb')
	
	for eachPath in finalMCCList:
		eachPath.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0], nodeID.split('CE')[1]))

		startTime = thisDict(eachPath[0])['cloudElementTime']
		endTime = thisDict(eachPath[-1])['cloudElementTime']
		duration = (endTime - startTime) + timedelta(hours=TRES)
		
		# convert datatime duration to seconds and add to the total for the average duration of all MCS in finalMCCList
		durations += (duration.total_seconds()) 
		
		#durations += duration
		startTimes.append(startTime)
		endTimes.append(endTime)

		#get the precip info
		#MCSPrecip = precipMaxMin(eachPath)

		for eachNode in eachPath:

			thisNode = thisDict(eachNode)

			#set first time min "fake" values
			if firstTime == True:
				# minCEprecipRate = MCSPrecip[0][1]
				# avgMinMCSPrecipRate = MCSPrecip[0][1]
				minCEprecipRate = thisNode['CETRMMmin']
				avgMinMCSPrecipRate += thisNode['CETRMMmin']
				firstTime = False

			#calculate the speed
			if thisNode['cloudElementArea'] >= OUTER_CLOUD_SHIELD_AREA:
				averagePropagationSpeed += findCESpeed(eachNode, eachPath)
				speedCounter +=1

			#Amax: find max area
			if thisNode['cloudElementArea'] > maxArea:
				maxArea = thisNode['cloudElementArea']
				# avgMaxArea += maxArea
				# maxAreaCounter += 1
				maxAreaTime = str(thisNode['cloudElementTime'])
				eccentricity = thisNode['cloudElementEccentricity']

				#determine the time the feature matures
				if matureFlag == True:
					timeMCSMatures = str(thisNode['cloudElementTime'])
					matureFlag = False

			#find min and max precip rate
			# minMax = list(value_tuple for node,value_tuple in enumerate(MCSPrecip) if value_tuple[0] == eachNode)
			# if minMax[0][1] < minCEprecipRate:
			# 	minCEprecipRate = minMax[0][1]
			# 	print "minCEprecipRate ", minCEprecipRate
			# if minMax[0][2] > maxCEprecipRate:
			# 	maxCEprecipRate = minMax[0][2]
			# 	print "maxCEprecipRate ", maxCEprecipRate
			if thisNode['CETRMMmin'] < minCEprecipRate:
				minCEprecipRate = thisNode['CETRMMmin']
				#print "minCEprecipRate ", minCEprecipRate
			if thisNode['CETRMMmax'] > maxCEprecipRate:
				maxCEprecipRate = thisNode['CETRMMmax']
				

			#calculations for only the mature stage
			if thisNode['nodeMCSIdentifier'] == 'M':
				#calculate average area of the maturity feature only 
				averageArea += thisNode['cloudElementArea']
				averageAreaCounter += 1
				durationOfMatureMCC +=1
				#precip total avg for only the mature stage
				# avgMaxPrecipRate += minMax[0][2]
				# avgMaxPrecipRateCounter += 1
				# avgMinPrecipRate += minMax[0][1]
				# avgMinPrecipRateCounter += 1
				# avgMaxMCSPrecipRate += minMax[0][2]
				# avgMaxMCSPrecipRateCounter += 1
				# avgMinMCSPrecipRate += minMax[0][1]
				# avgMinMCSPrecipRateCounter += 1
				avgMaxPrecipRate += thisNode['CETRMMmax']
				avgMaxPrecipRateCounter += 1
				avgMinPrecipRate += thisNode['CETRMMmin']
				avgMinPrecipRateCounter += 1
				avgMaxMCSPrecipRate += thisNode['CETRMMmax']
				avgMaxMCSPrecipRateCounter += 1
				avgMinMCSPrecipRate += thisNode['CETRMMmin']
				avgMinMCSPrecipRateCounter += 1

				#the precip percentage (TRMM area/CE area)
				if thisNode['cloudElementArea'] >= 0.0 and thisNode['TRMMArea'] >= 0.0:
					precipArea += thisNode['TRMMArea']
					avgPrecipArea.append(thisNode['TRMMArea'])
					avgPrecipAreaPercent += (thisNode['TRMMArea']/thisNode['cloudElementArea'])
					precipPercent.append((thisNode['TRMMArea']/thisNode['cloudElementArea'])) 
					precipCounter += 1

				#system speed for only mature stage
				CEspeed = findCESpeed(eachNode,eachPath)
				if CEspeed > 0.0 :
					MCSspeed += CEspeed
					MCSspeedCounter += 1
					
			#find accumulated precip
			if thisNode['cloudElementPrecipTotal'] > 0.0:
				MCSPrecipTotal += thisNode['cloudElementPrecipTotal']
				avgMCSPrecipTotalCounter +=1

		#A: calculate the average Area of the (mature) MCS
		if averageAreaCounter > 0: # and averageAreaCounter > 0:
			averageArea/= averageAreaCounter
			#averageAreas += averageArea
			averageAreas.append(averageArea)

		#v: MCS speed 
		if MCSspeedCounter > 0: # and MCSspeed > 0.0:
			MCSspeed /= MCSspeedCounter
			#print "MCSspeed ", MCSspeed, "MCSspeedCounter ", MCSspeedCounter

		#smallP_max: calculate the average max precip rate (mm/h)
		if avgMaxMCSPrecipRateCounter > 0 : #and avgMaxPrecipRate > 0.0:
			avgMaxMCSPrecipRate /= avgMaxMCSPrecipRateCounter
			#print "avgMaxMCSPrecipRate ", avgMaxMCSPrecipRate, "avgMaxMCSPrecipRateCounter ", avgMaxMCSPrecipRateCounter

		#smallP_min: calculate the average min precip rate (mm/h)
		if avgMinMCSPrecipRateCounter > 0 : #and avgMinPrecipRate > 0.0:
			avgMinMCSPrecipRate /= avgMinMCSPrecipRateCounter
			#print "avgMinMCSPrecipRate ", avgMinMCSPrecipRate, "avgMinMCSPrecipRateCounter ", avgMinMCSPrecipRateCounter

		#smallP_avg: calculate the average precipitation (mm hr-1)
		if MCSPrecipTotal > 0.0: # and avgMCSPrecipTotalCounter> 0:
			avgMCSPrecipTotal = MCSPrecipTotal/avgMCSPrecipTotalCounter
			avgPrecipTotal += avgMCSPrecipTotal
			avgPrecipTotalCounter += 1
			#print "avgPrecipTotal ", avgPrecipTotal, "avgPrecipTotalCounter ", avgPrecipTotalCounter

		#smallP_total = MCSPrecipTotal
		#precip over the MCS lifetime prep for bigP_total
		if MCSPrecipTotal > 0.0: 
			bigPtotal += MCSPrecipTotal
			bigPtotalCounter += 1
			#print "MCSPrecipTotal ", MCSPrecipTotal, " bigPtotal ", bigPtotal

		if maxArea > 0.0:
			avgMaxArea.append(maxArea)
			maxAreaCounter += 1

		#verage precipate area precentage (TRMM/CE area)
		if precipCounter > 0:
			avgPrecipAreaPercent /= precipCounter
			precipArea /= precipCounter


		#write stuff to file
		MCSUserFile.write("\n\n\nStarttime is: %s " %(str(startTime)))
		MCSUserFile.write("\nEndtime is: %s " %(str(endTime)))
		MCSUserFile.write("\nLife duration is %s hrs" %(str(duration)))
		MCSUserFile.write("\nTime of maturity is %s " %(timeMCSMatures))
		MCSUserFile.write("\nDuration mature stage is: %s " %durationOfMatureMCC*TRES)
		MCSUserFile.write("\nAverage area is: %.4f km^2 " %(averageArea))
		MCSUserFile.write("\nMax area is: %.4f km^2 " %(maxArea))
		MCSUserFile.write("\nMax area time is: %s " %(maxAreaTime))
		MCSUserFile.write("\nEccentricity at max area is: %.4f " %(eccentricity))
		MCSUserFile.write("\nPropagation speed is %.4f " %(MCSspeed))
		MCSUserFile.write("\nMCS minimum preicip rate is %.4f mmh^-1" %(minCEprecipRate))
		MCSUserFile.write("\nMCS maximum preicip rate is %.4f mmh^-1" %(maxCEprecipRate))
		MCSUserFile.write("\nTotal precipitation during MCS is %.4f mm/lifetime" %(MCSPrecipTotal))
		MCSUserFile.write("\nAverage MCS precipitation is %.4f mm" %(avgMCSPrecipTotal))
		MCSUserFile.write("\nAverage MCS maximum precipitation is %.4f mmh^-1" %(avgMaxMCSPrecipRate))
		MCSUserFile.write("\nAverage MCS minimum precipitation is %.4f mmh^-1" %(avgMinMCSPrecipRate))
		MCSUserFile.write("\nAverage precipitation area is %.4f km^2 " %(precipArea))
		MCSUserFile.write("\nPrecipitation area percentage of mature system %.4f percent " %(avgPrecipAreaPercent*100))


		#append stuff to lists for the summary file
		if MCSspeed > 0.0:
			allPropagationSpeeds.append(MCSspeed)
			averagePropagationSpeed += MCSspeed
			speedCounter += 1

		#reset vars for next MCS in list
		aaveragePropagationSpeed = 0.0
		#avgMaxArea = 0.0
		averageArea = 0.0
		averageAreaCounter = 0
		durationOfMatureMCC = 0
		MCSspeed = 0.0
		MCSspeedCounter = 0
		MCSPrecipTotal = 0.0
		avgMaxMCSPrecipRate =0.0
		avgMaxMCSPrecipRateCounter = 0
		avgMinMCSPrecipRate = 0.0
		avgMinMCSPrecipRateCounter = 0
		firstTime = True
		matureFlag = True
		avgMCSPrecipTotalCounter=0
		avgPrecipAreaPercent = 0.0
		precipArea = 0.0
		precipCounter = 0
		maxArea = 0.0
		maxAreaTime=''
		eccentricity = 0.0
		timeMCSMatures=''

	#LD: average duration
	if len(finalMCCList) > 1:
		durations /= len(finalMCCList)
		durations /= 3600.0 #convert to hours
	
		#A: average area
		#averageAreas /= len(finalMCCList)

		areaAvg = sum(averageAreas)/ len(finalMCCList)
	#create histogram plot here
	# if len(averageAreas) > 1:
	# 	plotHistogram(averageAreas, "Average Area [km^2]", "Area [km^2]")

	#Amax: average maximum area
	if maxAreaCounter > 0.0: #and avgMaxArea > 0.0 : 
		amax = sum(avgMaxArea)/ maxAreaCounter
		#create histogram plot here
		# if len(avgMaxArea) > 1:
		# 	plotHistogram(avgMaxArea, "Maximum Area [km^2]", "Area [km^2]")

	#v_avg: calculate the average propagation speed 
	if speedCounter > 0 :  # and averagePropagationSpeed > 0.0
		averagePropagationSpeed /= speedCounter
	
	#bigP_min: calculate the min rate in mature system
	if avgMinPrecipRate >  0.0: # and avgMinPrecipRateCounter > 0.0:
		avgMinPrecipRate /= avgMinPrecipRateCounter

	#bigP_max: calculate the max rate in mature system
	if avgMinPrecipRateCounter > 0.0: #and avgMaxPrecipRate >  0.0: 
		avgMaxPrecipRate /= avgMaxPrecipRateCounter

	#bigP_avg: average total preicip rate mm/hr
	if avgPrecipTotalCounter > 0.0: # and avgPrecipTotal > 0.0: 
		avgPrecipTotal /= avgPrecipTotalCounter

	#bigP_total: total precip rate mm/LD
	if bigPtotalCounter > 0.0: #and bigPtotal > 0.0: 
		bigPtotal /= bigPtotalCounter

	#precipitation area percentage
	if len(precipPercent) > 0:
		precipAreaPercent = (sum(precipPercent)/len(precipPercent))*100.0

	#average precipitation area
	if len(avgPrecipArea) > 0:
		precipAreaAvg = sum(avgPrecipArea)/len(avgPrecipArea)
		# if len(avgPrecipArea) > 1:
		# 	plotHistogram(avgPrecipArea, "Average Rainfall Area [km^2]", "Area [km^2]")
		

	#print "allPropagationSpeeds ",allPropagationSpeeds
	#print "averageTime(startTime) ", str(averageTime(startTimes))
	sTime = str(averageTime(startTimes))
	eTime = str(averageTime(endTimes))
	if len (allPropagationSpeeds) > 1:
		maxSpeed = max(allPropagationSpeeds)
		minSpeed = min(allPropagationSpeeds)
	else:
		maxSpeed = allPropagationSpeeds[0]
		minSpeed = allPropagationSpeeds[0]


	#write stuff to the summary file
	MCSSummaryFile.write("\nNumber of features is %d " %(len(finalMCCList)))
	MCSSummaryFile.write("\nAverage duration is %.4f hrs " %(durations))
	MCSSummaryFile.write("\nAverage startTime is %s " %(sTime[-8:]))
	MCSSummaryFile.write("\nAverage endTime is %s " %(eTime[-8:]))
	#MCSSummaryFile.write("\nAverage size is %.4f km^2 " %(averageAreas))
	MCSSummaryFile.write("\nAverage size is %.4f km^2 " %(areaAvg))
	MCSSummaryFile.write("\nAverage precipitation area is %.4f km^2 " %(precipAreaAvg))
	#MCSSummaryFile.write("\nAverage maximum size is %.4f km^2 " %(avgMaxArea))
	MCSSummaryFile.write("\nAverage maximum size is %.4f km^2 " %(amax))
	MCSSummaryFile.write("\nAverage propagation speed is %.4f ms^-1" %(averagePropagationSpeed))
	MCSSummaryFile.write("\nMaximum propagation speed is %.4f ms^-1 " %(maxSpeed))
	MCSSummaryFile.write("\nMinimum propagation speed is %.4f ms^-1 " %(minSpeed))
	MCSSummaryFile.write("\nAverage minimum precipitation rate is %.4f mmh^-1" %(avgMinPrecipRate))
	MCSSummaryFile.write("\nAverage maximum precipitation rate is %.4f mm h^-1" %(avgMaxPrecipRate))
	MCSSummaryFile.write("\nAverage precipitation is %.4f mm h^-1 " %(avgPrecipTotal))
	MCSSummaryFile.write("\nAverage total precipitation during MCSs is %.4f mm/LD " %(bigPtotal))
	MCSSummaryFile.write("\nAverage precipitation area percentage is %.4f percent " %(precipAreaPercent))


	MCSUserFile.close
	MCSSummaryFile.close
	return

#******************************************************************
#			PLOTTING UTIL SCRIPTS
#******************************************************************
def to_percent(y,position):
	'''
	'''
	return (str(100*y)+'%')
#******************************************************************
def colorbar_index(ncolors, nlabels, cmap):
	'''
	Taken from http://stackoverflow.com/questions/18704353/correcting-matplotlib-colorbar-ticks
	'''
	cmap = cmap_discretize(cmap, ncolors)
	mappable = cm.ScalarMappable(cmap=cmap)
	mappable.set_array([])
	mappable.set_clim(-0.5, ncolors+0.5)
	colorbar = plt.colorbar(mappable)#, orientation='horizontal')
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

    if type(cmap) == str:
        cmap = plt.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
                       for i in xrange(N+1) ]
    # Return colormap object.
    return mcolors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)
#******************************************************************
#			Deprecated over time
#******************************************************************
def isComplexTree(splitList, mergeList, mergeSplitList):
	'''
	Purpose:: Determine if a complex tree (with split and merge nodes) exist

	Input:: list of strings - splitList: list of all the nodes in the path that split
	        list of strings - mergeList: list of all the nodes in the path that merged
	        list of strings - mergeSplitList: list of split and merged nodes in the tree

	Output:: tuple (boolean, string) - complexTree: tuple with flag for if complexTree
										and string for the node

	Assumptions:: all passed lists are sorted

	'''

	counter = 0
	complexTreeFlag=False
	complexTreeNode=[]

	for thisNode in mergeList:
		# print "thisNode[0] ", thisNode[0]
		# print "mergeSplitList[counter] ", mergeSplitList[counter]
		# print "counter ", counter
		if mergeSplitList[counter] == thisNode[0]:
			counter +=1
			#complexTreeFlag=True
			complexMergeTree=thisNode[0]
		else:
			if counter > 1:
				complexTreeFlag=True
				break
	return (complexTreeFlag,complexTreeNode)	
#******************************************************************
def cloudElementSpeed (cloudElementCenterLat, cloudElementCenterLon):
	'''
	Purpose::
	    Determines the possible position of CE in the next frame
	    It assumes that it only moves towards the W, but may move N or S
	    Note that as this is called for a check of the CE with the prev F, 
	    it is a backward in space check (this calclation affects the lon only)
	`
	Input::
	    2 variables
		cloudElementCenterLat - float of the lat representing the CE center_of_mass
		cloudElementCenterLon - float of the lon representing the CE center_of_mass

	Output::
	    4 variables
	    minCElat - float of the lat representing the min  lat CE center_of_mass
	    minCElon - float of the lon representing the CE center_of_mass
	    maxCElat - float of the lat representing the max lat CE center_of_mass
	    maxCElon - float of the lon representing the max lon CE center_of_mass

	Assumptions::
	    The CE moves with the general flow (DIRECTION) as defined by the user. Of course, for smaller CEs this is not true,
	    hence limiting the usefulness of MCSs searches. But for climate applications, this is an ok limitation
	'''

	#if the lat is +ve substract u-component as we are considering backward trajectory
	if cloudElementCenterLat >= 0.0 :
		maxCElat = cloudElementCenterLat + (-1*MIN_CE_SPEED * math.sin(DIRECTION *math.pi/180.0)) /LAT_DISTANCE
		minCElat = cloudElementCenterLat + (-1*MAX_CE_SPEED * math.sin(DIRECTION *math.pi/180.0)) /LAT_DISTANCE
	else:
		maxCElat = cloudElementCenterLat - (-1*MIN_CE_SPEED * math.sin(DIRECTION *math.pi/180.0)) /LAT_DISTANCE
		minCElat = cloudElementCenterLat - (-1*MAX_CE_SPEED * math.sin(DIRECTION *math.pi/180.0)) /LAT_DISTANCE

	#if the lon is +ve substract the v-component as we are considering backward trajectory
	if cloudElementCenterLon >= 0.0:
		maxCElon = cloudElementCenterLon + (-1*MIN_CE_SPEED * math.cos(DIRECTION *math.pi/180.0)) /LON_DISTANCE
		minCElon = cloudElementCenterLon + (-1*MAX_CE_SPEED * math.cos(DIRECTION *math.pi/180.0)) /LON_DISTANCE
	else:
		maxCElon = cloudElementCenterLon - (-1*MIN_CE_SPEED * math.cos(DIRECTION *math.pi/180.0)) /LON_DISTANCE
		minCElon = cloudElementCenterLon - (-1*MAX_CE_SPEED * math.cos(DIRECTION *math.pi/180.0)) /LON_DISTANCE


	#print cloudElementCenterLat, cloudElementCenterLon
	#print "forecasted are" , minCElat, minCElon, maxCElat, maxCElon

	return minCElat, minCElon, maxCElat, maxCElon
#******************************************************************
def findMCS (prunedGraph):
	'''
	Purpose:: Determines if subtree is a MCC according to Laurent et al 1998 criteria

	Input:: a Networkx Graph - prunedGraph

    Output:: a list of dicts - finalMCCList: a list of list of nodes representing a MCC
   
    Assumptions: frames are ordered and are equally distributed in time e.g. hrly satellite images
 
	'''
	pathDictList =[]
	allMCSLists =[]
	allMCSListsTemp=[]
	
	MCSsFile = open((MAINDIRECTORY+'/textFiles/MCSsFile.txt'),'wb')

	#connected_components is not available for DiGraph, so generate graph as undirected 
	unDirGraph = PRUNED_GRAPH.to_undirected()
	subGraphNodes = nx.connected_components(unDirGraph)

	#for each path in the subgraphs determined
	for path in subGraphNodes:
		#order the values in the path according to the length of each string, the frame number, then the CE number
		path.sort(key=lambda nodeID:(len(nodeID.split('CE')[0]), nodeID.split('CE')[0], nodeID.split('CE')[1]))

		for node in path:
			pathDictList.append(thisDict(node))

		#create list of lists
		allMCSLists.append(list(pathDictList))
		allMCSListsTemp.append(path)
		pathDictList =[]

	for eachPath in allMCSListsTemp:
			eachPath.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0], nodeID.split('CE')[1]))
			MCSsFile.write("\n MCS is: %s " %eachPath)
	
	MCSsFile.close
	
	return allMCSLists 
#******************************************************************	
def removeListFromPath (aList,mainList,mergeSplitList):
	'''
	Purpose:: Utility script to remove a list of nodes from the path
	Input:: 3 lists
			aList - list of values to be deleted
			mainList - list for values to be deleted from
			mergeSplitList - list of nodes that are merged or split
	Output:: the edited list 
	'''

	for node in aList:
		try:
			#if the node is not  apart of the merge split list, then remove it...
			#this makes sure that merged/split nodes and paths aren't orphaned
			if not node in mergeSplitList:
				mainList.remove(node)
		except:
			print "node removed already"

	mainList.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
	
	return mainList
#******************************************************************
def generate_raw_values(sat_img):
    for index, value in np.ndenumerate(sat_img):
        print index, value
#******************************************************************
def generate_values(sat_img):
    for index, value in np.ndenumerate(sat_img):
        # Cast the 3 values in the index tuple to be used next
        time_index, lat_index, lon_index = index
        value_tuple =  (times[time_index], lat[lat_index], lon[lon_index], value)
        print value_tuple
#******************************************************************
def generateFinalList (thisList, fileName):
	'''
	    Purpose:: Utility function to provide final MCS or MCC list

		Input:: thisList - a list of list of strings or list of tuples (string, string)
		        NB: this list is global variable
				fileName - a string representing the fileName of where to store the info

		Output:: finalList - a list of dictionaries 
	'''
	finalListTemp =[]
	finalList =[]
	dictList =[]
	eachPathTemp=[]
	eachPathDict={}

	thisList.sort
	#print "thisList ", thisList

	#remove duplicates
	finalListTemp = map(list,set(map(tuple,thisList)))

	#print "finalListTemp ", finalListTemp

	#generate list of dictionaries 
	for eachPath in finalListTemp:
		#print "eachPath ", eachPath[0], type(eachPath[0])

		if type(eachPath[0]) is tuple:
			eachPathTemp = list(x[0] for x in eachPath)
			print "eachPathTemp in generateFinalList ", eachPathTemp
			eachPathDict = dict(eachPath)
			#eachPath.sort(key=lambda nodeID:(len(nodeID[0].split('C')[0]), nodeID[0].split('C')[0]))
		else:
			eachPathTemp = eachPath
		
		eachPathTemp.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))

		fileName.write("\n MCC is: %s " %eachPathTemp)
		#print "eachPath is: ", eachPathTemp 
		for eachNode in eachPathTemp:

			#print "eachNode in eachPath is: ", eachNode, eachPath
			if type(eachPath[0]) is tuple:
				#print "eachPathDict[eachNode] is ", eachPathDict[eachNode]
				addNodeMCSIdentifier(thisDict,eachPathDict[eachNode])
			#get node info and store in dictionary
			dictList.append(thisDict(eachNode))

		#create list of lists
		finalList.append(list(dictList))
		dictList=[]	

	return finalList
#******************************************************************
def simplestPathMCC (nodeList, CounterCriteriaA,CounterCriteriaB,potentialMCCList2):
	'''
	Purpose :: to determine if this path is a MCC

	Input:: list of nodes - nodeList: the nodes in the simple path 
			2 integers - CounterCriteriaA: # of consecutive nodes where criteriaA has been met
						 CounterCriteriaB: # of consecutive nodes where criteriaB has been met
			list of nodes - potentialMCCList2: list of nodes representing a possible MCC
			
	Output:: list of nodes - potentialMCCList2: list of nodes representing a possible MCC
			 2 integers - CounterCriteriaA: # of consecutive nodes where criteriaA has been met
						 CounterCriteriaB: # of consecutive nodes where criteriaB has been met
			list of nodes - checkedNodes: the nodes that have been visted whilst running this function

	Assumptions:: this list of paths has no merged or split nodes
	'''
	global MCCFLAG1 #= False #min requirements met for MCC
	MCCFLAG1 = False
	global MCCFLAG2 #= False #max requirements met for MCC
	MCCFLAG2 = False
	INITIATIONFLAG = True
	MATURITYFLAG = False
	DECAYFLAG = False
	
	thisdict = {} #will have the same items as the cloudElementDict = {'uniqueID', 'cloudElementLatLon', 'cloudElementCenter', 'cloudElementArea'}
	cloudElementArea = 0.0
	epsilon = 0.0
	MCCCritB = False
	appendedFlag = False
	appendedFlag1 = False
	maximumExtent = 0.0
	maximumExtentNode =''
	maximumExtentCriteria=[]
	oldNode=''
	checkedNodes=[]
	eachPathTemp=[]
	eachPathTemp1=[]
	overlap =[]
	potentialListTemp =[]
	#global definiteMCSMCCList

	print "in simplestPathMCC ---- "
	print "entering CounterCriteriaA, CounterCriteriaB ", CounterCriteriaA, CounterCriteriaB, potentialMCCList2

	if type(nodeList) is str:
		oldNode=nodeList
		nodeList =[]
		nodeList.append(oldNode)

	for node in nodeList:
		addNodeBehaviorIdentifier(node,'N')
		thisdict = thisDict(node)
		if thisdict['cloudElementArea'] >= OUTER_CLOUD_SHIELD_AREA:
			print "OUTER_CLOUD_SHIELD_AREA met by: ", node
			#if a CE for the same frame is not stored in the current MCC, then increment the counter
			# if not filter(lambda thisnode: thisnode.split('CE')[0] in node, potentialMCCList2):			
			# 	CounterCriteriaA += 1
			CounterCriteriaA += 1
		
			cloudElementArea,criteriaB = checkCriteriaB(thisdict['cloudElementLatLon'])
			
			#if Criteria A and B have been met, then the MCC is initiated, i.e. store node as potentialMCC
	   		if cloudElementArea >= INNER_CLOUD_SHIELD_AREA:
	   			# if not filter(lambda thisnode: thisnode.split('CE')[0] in node, potentialMCCList2):
	   			# 	CounterCriteriaB += 1
	   			CounterCriteriaB += 1
	   			potentialMCCList2.append(node)
	   			MCCFLAG1 = True
	   			#append this information on to the dictionary
	   			addInfothisDict(node, cloudElementArea, criteriaB)
	   			#updating MCSMCC list
	   			INITIATIONFLAG = False
	   			MATURITYFLAG = True
	   			"****adding node to potentialList, 'M'"
	   			potentialList.append((node,'M'))
	   			#potentialMCSMCCList.append((node,'M'))
				print "INNER_CLOUD_SHIELD_AREA met by: ", node
	   			print "potentialMCCList2 in INNER_CLOUD_SHIELD_AREA is: ", potentialMCCList2		
	   		else:
	   			CounterCriteriaB = 0
	   			CounterCriteriaA = 0
	   			potentialMCCList2=[]
	   			MCCFLAG1 = False
	   			MCCFLAG2 = False

	   			if INITIATIONFLAG == True:
	   				potentialList.append((node,'I'))
	   				"****adding node to potentialList, 'I'"
	   				#potentialMCSMCCList.append((node,'I'))
	   			elif INITIATIONFLAG == False and MATURITYFLAG == True:
	   				potentialList.append((node,'D'))
	   				"****adding node to potentialList, 'D'"
	   				#potentialMCSMCCList.append((node,'D'))
	   				DECAYFLAG = True
	   			
	   			print "no longer criteriaB", potentialMCCList2

	   		#duration check of MCC
	   		if CounterCriteriaB >= MINIMUM_DURATION and CounterCriteriaB <= MAXIMUM_DURATION:
	   			MCCCritB = True
	   		
	   		if (CounterCriteriaA >= MINIMUM_DURATION and MCCCritB == True) and (CounterCriteriaA <= MAXIMUM_DURATION):
	   			MCCFLAG2 = True
	   			print "duration criteria met"
	   			if thisdict['cloudElementArea'] >= maximumExtent:
	   				maximumExtentNode = node
	   				maximumExtent = thisdict['cloudElementArea']
	   				maximumExtentCriteria = criteriaB

	   			
	   			#populate definite MCC, note that potentialMCCList2 is updated with the new node already...
	   			if definiteMCC:
		   			currnode = [filter(lambda thisNode: not thisNode in potentialMCCList2, sublist) for sublist in definiteMCC]
		   			if currnode:
		   				for thisnode in currnode:
		   					#if the information has not been appended or added as yet, then try to add it
			   				if appendedFlag == False:			   					
				   				if thisnode and list(set(thisnode).difference(set(potentialMCCList2))) == node: 
				   					#print "in thisnode and list(set...) ", list(set(potentialMCCList2) - set(thisnode))[0]#definiteMCC[currnode.index(thisnode)]
				   					definiteMCC[currnode.index(thisnode)] = potentialMCCList2
				   					appendedFlag = True
				   					#print "definiteMCC in thisnode in currnode : ", definiteMCC
				   				#i.e. the list doesnt exist
				   				elif thisnode: # not (thisnode and list(set(thisnode).difference(set(potentialMCCList2)))) == False:
				   					#print "in else only thisnode exist"
				   					definiteMCC.append(potentialMCCList2)
				   					appendedFlag = True  						
			   		else:
			   			definiteMCC.append(potentialMCCList2)
			   			#print "definiteMCC in no currnode : ", definiteMCC
			   	else:
			   			definiteMCC.append(potentialMCCList2)
			   			#print "definiteMCC in no definiteMCC : ", definiteMCC

			checkedNodes.append(node)
			
		else:
			print "OUTER_CLOUD_SHIELD_AREA NOT met by: ", node
			checkedNodes.append(node)
			CounterCriteriaA = 0
			CounterCriteriaB = 0
			potentialMCCList2 = []   
			MCCFLAG2 = False
			MCCFLAG1 = False
			if INITIATIONFLAG == True:
				#print "****adding node to potentialList, 'I'"
				potentialList.append((node,'I'))
   				#potentialMCSMCCList.append((node,'I'))
   			elif INITIATIONFLAG==False and MATURITYFLAG == False:
   				#print "****adding node to potentialList, 'D'"
   				potentialList.append((node,'D'))
   				#potentialMCSMCCList.append((node,'D'))
   				DECAYFLAG = True

		#if potentialList and potentialMCCList2 overlap then update definiteMCSMCCList	
		potentialListTemp = list(y[0] for y in potentialList)
		#if there ia overlap between the potential MCS and the potential MCC
		if list(set(potentialListTemp) & set(potentialMCCList2)) and len(list(set(potentialListTemp) & set(potentialMCCList2))) >= MINIMUM_DURATION:
			
			if definiteMCSMCCList:
				#reset the temporary list of just the nodes
				eachPathTemp =[]

				for eachPath in definiteMCSMCCList:
					eachPathTemp.append(list(x[0] for x in eachPath))
					
				currnode = [filter(lambda thisNode: not thisNode in potentialListTemp, sublist) for sublist in eachPathTemp]
				
	   			if currnode:
	   				for thisnode in currnode:
	   					#if the information has not been appended or added as yet, then try to add it
		   				if appendedFlag1 == False: 
			   				if thisnode and list(set(thisnode).difference(set(potentialListTemp))) == node: 
			   					definiteMCSMCCList[currnode.index(thisnode)] = potentialList
			   					appendedFlag1 = True
			   				#i.e. the list doesnt exist
			   				elif thisnode: 
			   					definiteMCSMCCList.append(potentialList)
			   					appendedFlag1 = True   										 
			else:
				
				definiteMCSMCCList.append(potentialList)
				
	
	print "exiting simplestMCC CounterCriteriaA, CounterCriteriaB ", CounterCriteriaA, CounterCriteriaB
	print "MCCFLAG2 is: ", MCCFLAG2
	print "definiteMCC is: ", definiteMCC
	print "definiteMCSMCCList is: ", definiteMCSMCCList
	print "$$$ checkedNodes are ", checkedNodes
	print "---leaving simplestPathMCC() ----"

	return potentialMCCList2, CounterCriteriaA, CounterCriteriaB, checkedNodes
#******************************************************************
def simplestSplitPathMCC (path,CounterCriteriaA, CounterCriteriaB, currSplitNode, currMergedPart):
	'''
	Purpose: to determine if the MCC criteria was met in a subgraph that has splitting nodes

	Input:: list of nodes - path: the nodes in the path 
			2 integers - CounterCriteriaA: # of consecutive nodes where criteriaA has been met
						 CounterCriteriaB: # of consecutive nodes where criteriaB has been met
			string - currSplitNode: node that has more than one child
			list of strings - currMergedPart: list of nodes representing a possible MCC 
   
	Output:: 2 integers - CounterCriteriaAMergedPart: # of consecutive nodes where criteriaA has been met
						  CounterCriteriaBMergedPart: # of consecutive nodes where criteriaB has been met
			list of nodes - currMCC: list of nodes representing a possible MCC
			list of nodes - removeNodes: the nodes that have been visted whilst running this function

	Assumptions: the path has only splitting nodes
	'''
	shorterpath =[]
	splitMCC = False
	checkedNodes=[]
	removeNodes=[]
	maxCounterCriteriaA = 0
	maxCounterCriteriaB = 0

	#check if any of the paths after the split node are MCCs
	descend = PRUNED_GRAPH.successors(currSplitNode)
	print "descend is: ", descend, currSplitNode
	
	for node in descend:
		firstNode =[]
		shorterpath = []
		MCCSplitPart = True
		CounterCriteriaAMergedPart = 0
		CounterCriteriaBMergedPart = 0

		if not currSplitNode in currMergedPart:
			currMCC=[]
			CounterCriteriaA=0
			CounterCriteriaB =0
		else:
			currMCC = currMergedPart

		firstNode.append(node)
		shorterpath, numOfChildren = allDescendants(firstNode, node)
		if numOfChildren >1:
			print "in numOfChildren if"
			currSplitNode = shorterpath[-1]
			print "currSplitNode is: ", currSplitNode
			thisMCCMergedPart, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart,checkedNodes = simplestPathMCC(shorterpath, CounterCriteriaA, CounterCriteriaB, currMCC)
			print "recursive call in splitMCC"
			CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath,_ = simplestSplitPathMCC(shorterpath, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, currSplitNode, thisMCCMergedPart)
		else:
			print "in else for numOfChildren in simplestSplitPathMCC"
			MCCMergedPart, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart,checkedNodes = simplestPathMCC(shorterpath, CounterCriteriaA, CounterCriteriaB, currMCC)
		
		# if CounterCriteriaAMergedPart > maxCounterCriteriaA:
		# 	maxCounterCriteriaA = CounterCriteriaAMergedPart

		# if CounterCriteriaBMergedPart > maxCounterCriteriaB:
		# 	maxCounterCriteriaB = CounterCriteriaBMergedPart

		removeNodes.extend(checkedNodes)
	return CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, currMCC, removeNodes 
#******************************************************************
def simplestMergedPathMCC (path,CounterCriteriaA, CounterCriteriaB, mergeNode, currMergedPart):
	'''
	Purpose: to determine if the MCC criteria was met in a subgraph that has merging nodes

	Input:: list of nodes - path: the nodes in the path 
			2 integers - CounterCriteriaA: # of consecutive nodes where criteriaA has been met
						 CounterCriteriaB: # of consecutive nodes where criteriaB has been met
			string - mergeNode: node that has more than one child
			list of strings - currMergedPart: list of nodes representing a possible MCC 
    
	Output:: 2 integers - maxCounterCriteriaA: # of consecutive nodes where criteriaA has been met
						  maxCounterCriteriaB: # of consecutive nodes where criteriaB has been met
			list of nodes - currMCC: list of nodes representing a possible MCC
			list of nodes - removeNodes: the nodes that have been visted whilst running this function

	Assumptions: the path has only merging nodes
	'''
	shorterpath =[]
	currMCC =[]
	mergedMCC = False
	checkedNodes=[]
	removeNodes =[]
	mergeList=[]
	maxCounterCriteriaA = 0
	maxCounterCriteriaB = 0

	ascend = PRUNED_GRAPH.predecessors(mergeNode)
	print "ascend is: ", ascend, mergeNode, type(mergeNode)
	print "currMergedPart is: ", currMergedPart

	#TODO: remove the extra variable name currMCC is it needed?

	for node in ascend:
		#reset firstNode and path
		firstNode =[]
		shorterpath =[]
		MCCSplitPart = False
		CounterCriteriaASplitPart = 0
		CounterCriteriaBSplitPart = 0
		#if the node has already been accounted for in the possible MCC, this will happen for the 
		#worse case scenario, then don't check it again. if node not in traversal
		if node in currMergedPart:
			continue

		if not mergeNode  in currMergedPart:
			currMCC = []
			CounterCriteriaA = 0
			CounterCriteriaB = 0
		else:
			currMCC = currMergedPart

		print "currMCC in simplestMergedPathMCC for node in ascend is ", currMCC
		print "currMergedPart is: ", currMergedPart
		print "node is: ", node
		firstNode.append(node) 
		shorterpath, numOfParents = allAncestors(firstNode, node) 
		
		if numOfParents > 1:
			currMergedNode = shorterpath[-1]
			#find MCC possiblity of merged part alone
			thisMCCMergedPart,CounterCriteriaAMergedPart, CounterCriteriaBMergedPart,checkedNodes = simplestPathMCC(shorterpath,CounterCriteriaA,CounterCriteriaB, currMCC)
			path = removeListFromPath(checkedNodes,path,mergeList)
			
			#print " recursive call!! firstNode, and currMergedNode are: ",firstNode , currMergedNode
			CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath,_ = simplestMergedPathMCC (shorterpath, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, currMergedNode,thisMCCMergedPart) 
		else:
			print "***^^^CoutnercriteriaA and CountercriteriaB are", CounterCriteriaA, CounterCriteriaB, shorterpath, currMCC
			#find for just that path...NB, it is checking backwards, thus we can add in the merged part
			MCCSplitPart, CounterCriteriaASplitPart, CounterCriteriaBSplitPart,checkedNodes = simplestPathMCC(shorterpath,CounterCriteriaA,CounterCriteriaB, currMCC)
			
		if CounterCriteriaASplitPart > maxCounterCriteriaA:
			maxCounterCriteriaA = CounterCriteriaASplitPart

		if CounterCriteriaBSplitPart > maxCounterCriteriaB:
			maxCounterCriteriaB = CounterCriteriaBSplitPart

		removeNodes.extend(checkedNodes)
	return maxCounterCriteriaA, maxCounterCriteriaB, currMCC, removeNodes
#******************************************************************
def splitMergedPathMCC (path,CounterCriteriaA, CounterCriteriaB, mergeSplitList, complexTree):
	'''
	Purpose: to determine if the MCC criteria was met in a subgraph that has splitting and merging nodes

	Input:: list of strings - path: the nodes in the path 
			2 integers - CounterCriteriaA: # of consecutive nodes where criteriaA has been met
						 CounterCriteriaB: # of consecutive nodes where criteriaB has been met
			list of strings - mergeSplitList: list of nodes representing the split and merged nodes in the subgraph
			tuple (boolean, string) - complexTree: tuple representing if complexTree 
	Output:: NONE

	Assumptions: passed list are ordered
	'''
	shorterpath =[]
	currMCC =[]
	mergedMCC = False
	traversal ={}
	possibleMCC =[]
	potentialMCCList1 =[]
	MCCMergedPart =[]
	tempPath =[]
	mergeOrSplitInMCC =[]
	temp =''
	
	complexTreeFlag = complexTree [0]
	complexTreeNode = complexTree[1]

	tempPath = path
	count = 0
	#complex merging tree scenario
	if complexTreeFlag==True:
		print "!!! complexMergeTree !!!"
		if mergeSplitList:
			mergeSplitList.remove(complexTreeNode)
			print "removed merged node ", complexTreeNode," from mergeSplitList ", mergeSplitList
		MCCMergedPart,CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, checkedNodes = simplestPathMCC(complexTreeNode,CounterCriteriaA,CounterCriteriaB, potentialMCCList1)
		if node in MCCMergedPart:
			mergeOrSplitInMCC.append(complexTreeNode)
			print "added node to mergeOrSplitInMCC"
		print "checkedNodes are ", checkedNodes
		path = removeListFromPath(checkedNodes,path, mergeSplitList)	
		print "running simplestMergedPathMCC ", CounterCriteriaAMergedPart, CounterCriteriaBMergedPart
		CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath, removeNodes = simplestMergedPathMCC (path, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, currMergedNode, MCCMergedPart)
		#remove shorterpath from path
		path = removeListFromPath(removeNodes,path,mergeSplitList)	
		tempPath = path
					

	while tempPath:
		#path.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
		count = 0
		for node in path:
			print "in node for loop for path", node, "count is ", count
			print "tempPath is ", tempPath, type(tempPath)
			print "tempPath[0] is ", tempPath[count]	
			if type(tempPath) is str:
				temp = tempPath
				tempPath=[]
				tempPath.append(temp)
				temp = ''

			if node == tempPath[count]:		
				#check if it meets the criteria
				mergedCount = PRUNED_GRAPH.in_degree(node)
				splitCount = PRUNED_GRAPH.out_degree(node)

				print "mergedCount and splitCount are: ", mergedCount, splitCount

				shorterpath.append(node)
				count += 1
				
				if splitCount > 1 and mergedCount <= 1: #i.e. node is split only
					if mergeSplitList:
						if node == mergeSplitList[0]:
							print "first is a split", node, mergeSplitList[0]
							beforeSplitNodeIndex = 0
							shorterpath =[]
							shorterpath,_ = allAncestors(node,node) #path[beforeSplitNodeIndex:path.index(node)+1]
						
						mergeSplitList.remove(node)
						print "removed split node ", node," from mergeSplitList ", mergeSplitList
			
					#find MCC possiblity of merged part before the split
					print " in worse SCENARIO with split and simpleMCCPath call with ", shorterpath, CounterCriteriaA, CounterCriteriaB
					if type(shorterpath) is str:
						temp = shorterpath
						shorterpath =[]
						shorterpath.append(temp)
						temp =''

					shorterpath.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
					MCCMergedPart,CounterCriteriaAMergedPart, CounterCriteriaBMergedPart,checkedNodes = simplestPathMCC(shorterpath,CounterCriteriaA,CounterCriteriaB, potentialMCCList1)
					print "checkedNodes are ", checkedNodes
					#remove path from list
					path = removeListFromPath(checkedNodes,path,mergeSplitList)
					tempPath = removeListFromPath(checkedNodes,path,mergeSplitList)	
					splitNode = node
					print "running simplestSplitPathMCC ", CounterCriteriaAMergedPart, CounterCriteriaBMergedPart

					CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath, removeNodes = simplestSplitPathMCC (path, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, splitNode, MCCMergedPart)
					#remove shorterpath from path
					path = removeListFromPath(removeNodes,path, mergeSplitList)
					tempPath = removeListFromPath(checkedNodes,path, mergeSplitList)
						
					shorterpath=[]
					CounterCriteriaA = CounterCriteriaASplitPart
					CounterCriteriaB = CounterCriteriaBSplitPart
					count = 0

				elif (mergedCount > 1 and splitCount <= 1) or (mergedCount > 1 and splitCount >1): #node can be merged and split
					#remove node from the mergesplit list
					#try:
					print " in worse SCENARIO with merge and simpleMCCPath call with ", shorterpath, CounterCriteriaA, CounterCriteriaB
					
					if mergeSplitList:
						mergeSplitList.remove(node)
						print "removed merged node ", node," from mergeSplitList ", mergeSplitList
					#except:
					#find MCC possiblity of merged part alone, add on the next node
					#dirty fix to check that the running counter is indeed valid
					# if not node in potentialMCCList1:
					# 	CounterCriteriaA = 0 
					# 	CounterCriteriaB = 0
					shorterpath.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))
					MCCMergedPart,CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, checkedNodes = simplestPathMCC(node,CounterCriteriaA,CounterCriteriaB, potentialMCCList1)
					if node in MCCMergedPart:
						mergeOrSplitInMCC.append(node)
						print "added node to mergeOrSplitInMCC"

					print "checkedNodes are ", checkedNodes
					path = removeListFromPath(checkedNodes,path, mergeSplitList)	
					tempPath = removeListFromPath(checkedNodes,path,mergeSplitList)
					
					currMergedNode = node
					print "running simplestMergedPathMCC ", CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, mergeOrSplitInMCC
					#dirty fix to check that the running counter is indeed valid
					if mergeOrSplitInMCC:
						print "mergeOrSplitInMCC is ", mergeOrSplitInMCC
						if not mergeOrSplitInMCC[-1] in MCCMergedPart:
							CounterCriteriaAMergedPart = 0 
							CounterCriteriaBMergedPart = 0
					
					print "running simplestMergedPathMCC ", CounterCriteriaAMergedPart, CounterCriteriaBMergedPart

					CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath, removeNodes = simplestMergedPathMCC (path, CounterCriteriaAMergedPart, CounterCriteriaBMergedPart, currMergedNode, MCCMergedPart)
					#remove shorterpath from path
					path = removeListFromPath(removeNodes,path,mergeSplitList)	
					tempPath = removeListFromPath(checkedNodes,path,mergeSplitList)

					shorterpath =[]
					CounterCriteriaA = CounterCriteriaASplitPart
					CounterCriteriaB = CounterCriteriaBSplitPart
					count = 0

					if splitCount > 1:
						splitNode = node
						print "in split after merge ", CounterCriteriaA, CounterCriteriaB
						CounterCriteriaASplitPart, CounterCriteriaBSplitPart, shorterpath, removeNodes = simplestSplitPathMCC (path, CounterCriteriaA, CounterCriteriaB, splitNode, MCCMergedPart)
						#remove shorterpath from path
						path = removeListFromPath(removeNodes,path,mergeSplitList)
						tempPath = removeListFromPath(checkedNodes,path,mergeSplitList)
							
						shorterpath=[]
						CounterCriteriaA = CounterCriteriaASplitPart
						CounterCriteriaB = CounterCriteriaBSplitPart
				else:
					print "^^^^^^^^^^^ in neither split of merged only"
					MCCMergedPart,CounterCriteriaAMergedPart, CounterCriteriaBMergedPart,checkedNodes = simplestPathMCC(shorterpath,CounterCriteriaA,CounterCriteriaB, potentialMCCList1)
					tempPath = removeListFromPath(checkedNodes, path, mergeSplitList)

			else:
				# the node != tempPath[count]
				continue

			path.sort(key=lambda nodeID:(len(nodeID.split('C')[0]), nodeID.split('C')[0]))

		print "next node in for path", tempPath

	return 
#******************************************************************


			

