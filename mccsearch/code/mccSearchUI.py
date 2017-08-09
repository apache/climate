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
'''
# Wizard for running the mccSearch program
'''

import os
import networkx as nx
# mccSearch modules
from mccSearch import *


def main():
    CEGraph = nx.DiGraph()
    prunedGraph = nx.DiGraph()
    MCCList = []
    MCSList = []
    MCSMCCNodesList = []
    allMCSsList = []
    allCETRMMList = []
    DIRS = {}
    # DIRS={
    #          mainDirStr= "/directory/to/where/to/store/outputs"
    #          TRMMdirName = "/directory/to/the/TRMM/netCDF/files"
    #          CEoriDirName = "/directory/to/the/MERG/netCDF/files"
    #         }
    preprocessing = ''
    rawMERG = ''

    print("Running MCCSearch ..... \n")
    # This is where data created will be stored
    DIRS['mainDirStr'] = input("> Please enter working directory: \n")

    # preprocessing = raw_input ("> Do you need to preprocess the MERG files? [y/n]: \n")
    # while preprocessing.lower() != 'n':
    #     if preprocessing.lower() == 'y':
    #         #get location for raw files
    #         rawMERG = raw_input("> Please enter the directory to the RAW MERG (.Z) files: \n")
    #         #run preprocessing
    #         mccSearch.preprocessingMERG(rawMERG)
    #         continue
    #     elif preprocessing.lower() == 'n' :
    #         pass
    #     else:
    #         print("Error! Invalid choice.")
    #         preprocessing = raw_input ("> Do you need to preprocess the MERG files? [y/n]: \n")

    # get the location of the MERG and TRMM data
    DIRS['CEoriDirName'] = input(
        "> Please enter the directory to the MERG netCDF files: \n")

    try:
        if not os.path.exists(DIRS['CEoriDirName']):
            print("Error! MERG invalid path!")
            DIRS['CEoriDirName'] = input(
                "> Please enter the directory to the MERG netCDF files: \n")
    except BaseException:
        print("...")

    DIRS['TRMMdirName'] = input(
        "> Please enter the location to the raw TRMM netCDF files: \n")
    try:
        if not os.path.exists(DIRS['TRMMdirName']):
            print("Error: TRMM invalid path!")
            DIRS['TRMMdirName'] = input(
                "> Please enter the location to the raw TRMM netCDF files: \n")
    except BaseException:
        pass

    # get the dates for analysis
    startDateTime = input(
        "> Please enter the start date and time yyyymmddhr: \n")
    # check validity of time
    while validDate(startDateTime) == 0:
        print("Invalid time entered for startDateTime!")
        startDateTime = input(
            "> Please enter the start date and time yyyymmddhr: \n")

    endDateTime = input("> Please enter the end date and time yyyymmddhr: \n")
    while validDate(endDateTime) == 0:
        print("Invalid time entered for endDateTime!")
        endDateTime = input(
            "> Please enter the end date and time yyyymmddhr: \n")

    # check if all the files exisits in the MERG and TRMM directories entered
    test, _ = mccSearch.checkForFiles(
        startDateTime, endDateTime, DIRS['TRMMdirName'], 2)
    if not test:
        print("Error with files in the original TRMM directory entered. Please check your files before restarting.")
        return
    test, filelist = mccSearch.checkForFiles(
        startDateTime, endDateTime, DIRS['CEoriDirName'], 1)
    if not test:
        print("Error with files in the original MERG directory entered. Please check your files before restarting.")
        return

    # create main directory and file structure for storing intel
    mccSearch.createMainDirectory(DIRS['mainDirStr'])
    TRMMCEdirName = DIRS['mainDirStr'] + '/TRMMnetcdfCEs'
    CEdirName = DIRS['mainDirStr'] + '/MERGnetcdfCEs'

    # for doing some postprocessing with the clipped datasets instead of
    # running the full program, e.g.
    postprocessing = input("> Do you wish to postprocess data? [y/n] \n")
    while postprocessing.lower() != 'n':
        if postprocessing.lower() == 'y':
            option = postProcessingplotMenu(DIRS)
            return
        elif postprocessing.lower() == 'n':
            pass
        else:
            print("\n Invalid option.")
            postprocessing = input(
                "> Do you wish to postprocess data? [y/n] \n")
    # -------------------------------------------------------------------------------------------------
    # Getting started. Make it so number one!
    print(("-" * 80))
    print("\t\t Starting the MCCSearch Analysis.")
    print(("-" * 80))
    print("\n -------------- Reading MERG and TRMM Data ----------")
    mergImgs, timeList = mccSearch.readMergData(DIRS['CEoriDirName'], filelist)
    print("\n -------------- findCloudElements ----------")
    CEGraph = mccSearch.findCloudElements(
        mergImgs, timeList, DIRS['TRMMdirName'])
    # if the TRMMdirName wasnt entered for whatever reason, you can still get the TRMM data this way
    # CEGraph = mccSearch.findCloudElements(mergImgs,timeList)
    # allCETRMMList=mccSearch.findPrecipRate(DIRS['TRMMdirName'],timeList)
    # ----------------------------------------------------------------------------------------------
    print("\n -------------- findCloudClusters ----------")
    prunedGraph = mccSearch.findCloudClusters(CEGraph)
    print("\n -------------- findMCCs ----------")
    MCCList, MCSList = mccSearch.findMCC(prunedGraph)
    # now ready to perform various calculations/metrics
    print(("-" * 80))
    print("\n -------------- METRICS ----------")
    print(("-" * 80))
    # some calculations/metrics that work that work
    print(("creating the MCC userfile ", mccSearch.createTextFile(MCCList, 1)))
    print(("creating the MCS userfile ", mccSearch.createTextFile(MCSList, 2)))
    plotMenu(MCCList, MCSList)

    # Let's get outta here! Engage!
    print(("-" * 80))
#*************************************************************************


def plotMenu(MCCList, MCSList):
    '''
    Purpose:: The flow of plots for the user to choose

    Input:: MCCList: a list of directories representing a list of nodes in the MCC
            MCSList: a list of directories representing a list of nodes in the MCS

    Output:: None
    '''
    option = displayPlotMenu()
    while option != 0:
        try:
            if option == 1:
                print(
                    "Generating Accumulated Rainfall from TRMM for the entire period ...\n")
                mccSearch.plotAccTRMM(MCSList)
            if option == 2:
                startDateTime = input(
                    "> Please enter the start date and time yyyy-mm-dd_hr:mm:ss format: \n")
                endDateTime = input(
                    "> Please enter the end date and time yyyy-mm-dd_hr:mm:ss format: \n")
                print(("Generating acccumulated rainfall between ",
                       startDateTime, " and ", endDateTime, " ... \n"))
                mccSearch.plotAccuInTimeRange(startDateTime, endDateTime)
            if option == 3:
                print("Generating area distribution plot ... \n")
                mccSearch.displaySize(MCCList)
            if option == 4:
                print("Generating precipitation and area distribution plot ... \n")
                mccSearch.displayPrecip(MCCList)
            if option == 5:
                try:
                    print("Generating histogram of precipitation for each time ... \n")
                    mccSearch.plotPrecipHistograms(MCCList)
                except BaseException:
                    pass
        except BaseException:
            print("Invalid option. Please try again, enter 0 to exit \n")

        option = displayPlotMenu()
    return
#*************************************************************************


def displayPlotMenu():
    '''
    Purpose:: Display the plot Menu Options

    Input:: None

    Output:: option: an integer representing the choice of the user
    '''
    print("**************** PLOTS ************** \n")
    print("0. Exit \n")
    print("1. Accumulated TRMM precipitation \n")
    print("2. Accumulated TRMM precipitation between dates \n")
    print("3. Area distribution of the system over time \n")
    print("4. Precipitation and area distribution of the system \n")
    print("5. Histogram distribution of the rainfall in the area \n")
    option = int(input("> Please enter your option for plots: \n"))
    return option
#*************************************************************************


def displayPostprocessingPlotMenu():
    '''
    Purpose:: Display the plot Menu Options

    Input:: None

    Output:: option: an integer representing the choice of the user
    '''
    print("**************** POST PROCESSING PLOTS ************** \n")
    print("0. Exit \n")
    print("1. Map plots of the original MERG data \n")
    print("2. Map plots of the cloud elements using IR data \n")
    print("3. Map plots of the cloud elements rainfall accumulations using TRMM data \n")
    #print("4. Accumulated TRMM precipitation \n")
    #print("5. Accumulated TRMM precipitation between dates \n")

    option = int(input("> Please enter your option for plots: \n"))
    return option
#*************************************************************************


def postProcessingplotMenu(DIRS):
    '''
    Purpose:: The flow of plots for the user to choose

    Input:: DIRS a dictionary of directories
    #       DIRS={
    #          mainDirStr= "/directory/to/where/to/store/outputs"
    #          TRMMdirName = "/directory/to/the/TRMM/netCDF/files"
    #          CEoriDirName = "/directory/to/the/MERG/netCDF/files"
    #         }

    Output:: None
    '''
    TRMMCEdirName = DIRS['mainDirStr'] + '/TRMMnetcdfCEs'
    CEdirName = DIRS['mainDirStr'] + '/MERGnetcdfCEs'

    option = displayPostprocessingPlotMenu()
    while option != 0:
        try:
            if option == 1:
                print("Generating images from the original MERG dataset ... \n")
                mccSearch.postProcessingNetCDF(1, DIRS['CEoriDirName'])
            if option == 2:
                print(
                    "Generating images from the cloud elements using MERG IR data ... \n")
                mccSearch.postProcessingNetCDF(2, CEdirName)
            if option == 3:
                print(
                    "Generating precipitation accumulation images from the cloud elements using TRMM data ... \n")
                mccSearch.postProcessingNetCDF(3, TRMMCEdirName)
            # if option == 4:
            #     print("Generating Accumulated TRMM rainfall from cloud elements for each MCS ... \n")
            #     featureType = int(raw_input("> Please enter type of MCS MCC-1 or MCS-2: \n"))
            #     if featureType == 1:
            #         filename = DIRS['mainDirStr']+'/textFiles/MCCPostProcessing.txt'
            #         try:
            #             if os.path.isfile(filename):
            #             #read each line as a list
            #         mccSearch.plotAccTRMM()
            # if option == 5:
            #     mccSearch.plotAccuInTimeRange()
        except BaseException:
            print("Invalid option, please try again")
        option = displayPostprocessingPlotMenu()
    return
#*************************************************************************


def validDate(dataString):
    '''
    '''

    if len(dataString) > 10:
        print("invalid time entered")
        return 0

    yr = int(dataString[:4])
    mm = int(dataString[4:6])
    dd = int(dataString[6:8])
    hh = int(dataString[-2:])

    if mm < 1 or mm > 12:
        return 0
    elif hh < 0 or hh > 23:
        return 0
    elif (dd < 0 or dd > 30) and (mm == 4 or mm == 6 or mm == 9 or mm == 11):
        return 0
    elif (dd < 0 or dd > 31) and (mm == 1 or mm == 3 or mm == 5 or mm == 7 or mm == 8 or mm == 10):
        return 0
    elif dd > 28 and mm == 2 and (yr % 4) != 0:
        return 0
    elif (yr % 4) == 0 and mm == 2 and dd > 29:
        return 0
    elif dd > 31 and mm == 12:
        return 0
    else:
        return 1
#*************************************************************************


main()
