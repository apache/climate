#!/usr/local/python27
""" DOCSTRING"""

# Python Standard Lib Imports
import argparse
import ConfigParser
import datetime
import glob
import os
import sys
import numpy as np
import numpy.ma as ma


# RCMES Imports
import storage.rcmed as db
from toolkit import do_data_prep, process, metrics
from utils import misc
from classes import JobProperties, Model, GridBox
from cli import rcmet_ui as ui

parser = argparse.ArgumentParser(description='Regional Climate Model Evaluation Toolkit.  Use -h for help and options')
parser.add_argument('-c', '--config', dest='CONFIG', help='Path to an evaluation configuration file')
args = parser.parse_args()

def checkConfigSettings(config):
    """ This function will check the SETTINGS block of the user supplied config file.
    This will only check if the working and cache dirs are writable from this program.
    Additional configuration parameters can be checked here later on.
    
    Input::
        config - ConfigParser configuration object
    
    Output::
        none - An exception will be raised if something goes wrong
    """
    settings = config.items('SETTINGS')
    for key_val in settings:
        # Check the user provided directories are valid
        if key_val[0] == 'workDir' or key_val[0] == 'cacheDir':
            _ =  misc.isDirGood(os.path.abspath(key_val[1]))

        else:
            pass    

def setSettings(settings, config):
    """
    This function is used to set the values within the 'SETTINGS' dictionary when a user provides an external
    configuration file.
    
    Input::
        settings - Python Dictionary object that will collect the key : value pairs
        config - A configparse object that contains the external config values
    
    Output::
        None - The settings dictionary will be updated in place.
    """
    pass

def generateModels(modelConfig):
    """
    This function will return a list of Model objects that can easily be used for 
    metric computation and other processing tasks.
    
    Input::  
        modelConfig - list of ('key', 'value') tuples.  Below is a list of valid keys
            filenamepattern - string i.e. '/nas/run/model/output/MOD*precip*.nc'
            latvariable - string i.e. 'latitude'
            lonvariable - string i.e. 'longitude'
            timevariable - string i.e. 't'
            timestep - string 'monthly' | 'daily' | 'annual'
            varname - string i.e. 'pr'

    Output::
        modelList - List of Model objects
    """
    # Setup the config Data Dictionary to make parsing easier later
    configData = {}
    for entry in modelConfig:
        configData[entry[0]] = entry[1]

    modelFileList = None
    for keyValTuple in modelConfig:
        if keyValTuple[0] == 'filenamePattern':
            modelFileList = glob.glob(keyValTuple[1])
            modelFileList.sort()

    # Remove the filenamePattern from the dict since it is no longer used
    configData.pop('filenamePattern')
    
    models = []
    for modelFile in modelFileList:
        # use getModelTimes(modelFile,timeVarName) to generate the modelTimeStep and time list
        _ , configData['timeStep'] = process.getModelTimes(modelFile, configData['timeVariable'])
        configData['filename'] = modelFile
        model = Model(**configData)
        models.append(model)
    
    return models

def generateSettings(config):
    """
    Helper function to decouple the argument parsing from the Settings object creation
    
    Input::  
        config - list of ('key', 'value') tuples.
            workdir - string i.e. '/nas/run/rcmet/work/'
            cachedir - string i.e. '/tmp/rcmet/cache/'
    Output::
        JobProperties - JobProperties Object
    """
    # Setup the config Data Dictionary to make parsing easier later
    configData = {}
    for entry in config:
        configData[entry[0]] = entry[1]
        
    return JobProperties(**configData)

def makeDatasetsDictionary(rcmedConfig):
    """
    Helper function to decouple the argument parsing from the RCMEDDataset object creation

    Input::  
        rcmedConfig - list of ('key', 'value') tuples.
            obsDatasetId=3,10
            obsParamId=36,32
            obsTimeStep=monthly,monthly

    Output::
        datasetDict - Dictionary with dataset metadata
    # Setup the config Data Dictionary to make parsing easier later
    """
    delimiter = ','
    configData = {}
    for entry in rcmedConfig:
        if delimiter in entry[1]:
            # print 'delim found - %s' % entry[1]
            valueList = entry[1].split(delimiter)
            configData[entry[0]] = valueList
        else:
            configData[entry[0]] = entry[1:]

    return configData

def tempGetYears():
    startYear = int(raw_input('Enter start year YYYY \n'))
    endYear = int(raw_input('Enter end year YYYY \n'))
    # CGOODALE - Updating the Static endTime to be 31-DEC
    startTime = datetime.datetime(startYear, 1, 1, 0, 0)
    endTime = datetime.datetime(endYear, 12, 31, 0, 0)
    return (startTime, endTime)


def runUsingConfig(argsConfig):
    """
    This function is called when a user provides a configuration file to specify an evaluation job.

    Input::
        argsConfig - Path to a ConfigParser compliant file

    Output::
        Plots that visualize the evaluation job. These will be output to SETTINGS.workDir from the config file
    """
    
    print 'Running using config file: %s' % argsConfig
    # Parse the Config file
    userConfig = ConfigParser.SafeConfigParser()
    userConfig.optionxform = str # This is so the case is preserved on the items in the config file
    userConfig.read(argsConfig)

    try:
        checkConfigSettings(userConfig)
    except:
        raise

    jobProperties = generateSettings(userConfig.items('SETTINGS'))
    workdir = jobProperties.workDir
    
    try:
        gridBox = GridBox(jobProperties.latMin, jobProperties.lonMin, jobProperties.latMax,
                          jobProperties.lonMax, jobProperties.gridLonStep, jobProperties.gridLatStep)
    except:
        gridBox = None

    models = generateModels(userConfig.items('MODEL'))
    
    # 5/28/2013, JK: The RCMED block has been modified to accommodate ref data input from users' local disk

    datasetDict = makeDatasetsDictionary(userConfig.items('RCMED'))


    # Go get the parameter listing from the database
    try:
        params = db.get_parameters_metadata()
    except:
        raise

    obsDatasetList = []
    obsList = []
    obsVarName = datasetDict['obsVarName'][0]
    obsTimeName = datasetDict['obsTimeVar'][0]
    obsLonName = datasetDict['obsLonVar'][0]
    obsLatName = datasetDict['obsLatVar'][0]
    obsTimestep = []
    obsSource = int(datasetDict['obsSource'][0])
    #print 'Obs datasetDict'
    #print datasetDict

    if obsSource < 0:                             # no obs data to be processed
        obsVarName = []
        obsTimeName = []
        obsLonName = []
        obsLatName = []
    elif obsSource == 0:                          # input from RCMED
        for param_id in datasetDict['obsParamId']:
            for param in params:
                if int(param['parameter_id']) == int(param_id):
                    obsDatasetList.append(param)
                else:
                    pass
    elif obsSource == 1:                        # input from local disk
        for param in datasetDict['obsInputFile']:
            obsDatasetList.append(param)
        for param in datasetDict['obsFileName']:
            obsList.append(param)
        for param in datasetDict['obsDltaTime']:
            obsTimestep.append(param)
    #print obsSource,obsDatasetList,obsList,obsTimeName,obsTimestep

    #TODO: Unhardcode this when we decided where this belongs in the Config File
    jobProperties.maskOption = True
    # User must provide startTime and endTime if not defined
    if jobProperties.startDate == None or jobProperties.endDate == None:
        jobProperties.startDate,jobProperties.endDate = misc.userDefinedStartEndTimes(obsSource,obsList,obsTimeName,obsDatasetList,models)

    numOBS,numMDL,nT,ngrdY,ngrdX,Times,lons,lats,obsData,mdlData,obsName,mdlName,varType = do_data_prep.prep_data   \
          (jobProperties,obsSource,obsDatasetList,obsList,obsVarName,obsLonName,obsLatName,obsTimeName,obsTimestep,gridBox,models)

    # 6/3/2013: Combine the regridded reference and model datasets. The packing order is: 
    #               First pack all ref (obs) data with the ref enseble in the end (if exists).
    #               Then pack all model data with the model ensemble in the end (if exists)
    #           Release 'obsData' and 'mdlData' after their values are transferred to 'allData'
    print 'Input and regridding of both obs and model data are completed. Combine the obs and model data'
    numDatasets = numOBS + numMDL
    allData = ma.zeros((numDatasets, nT, ngrdY, ngrdX))
    if (numOBS>0) & (numMDL>0):
        dataName = obsName + mdlName
        allData[0:numOBS, :, :, :] = obsData[0:numOBS, :, :, :]
        allData[numOBS:numDatasets, :, :, :] = mdlData[0:numMDL, :, :, :]
        obsData = 0.
        mdlData = 0.
    elif numOBS==0:
        dataName = mdlName
        allData = mdlData
        mdlData = 0.
    else:
        dataName = obsName
        allData = obsData
        obsData = 0
    print ''
    print 'dataName: ',dataName,' shape of all data= ',allData.shape

    ##################################################################################
    # calculate metrics and make plots using the regridded reference and model data. #
    ##################################################################################
    print 'Data preparation is completed; now move to metrics calculations'
    
    try:
        subRegionConfig = misc.configToDict(userConfig.items('SUB_REGION'))
        subRegions = misc.parseSubRegions(subRegionConfig)
        # REORDER SUBREGION OBJECTS until we standardize on Python 2.7
        # TODO Remove once Python 2.7 support is finalized
        if subRegions:
            subRegions.sort(key=lambda x:x.name)
        
    except ConfigParser.NoSectionError:
        
        counts = {'observations': numOBS,
                  'models'      : numMDL,
                  'times'       : nT}
        subRegions = misc.getSubRegionsInteractively(counts, workdir)
        
        if len(subRegions) == 0:
            print 'Processing without SubRegion support'
        

    # TODO: New function Call
    timeRegridOption = jobProperties.temporalGrid
    fileOutputOption = jobProperties.writeOutFile
    modelVarName = models[0].varName
    metrics.metrics_plots(modelVarName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, allData, dataName, workdir, subRegions, \
                          timeRegridOption, fileOutputOption, varType)


if __name__ == "__main__":
    
    if args.CONFIG:
        
        runUsingConfig(args.CONFIG)

    else:
        print 'Interactive mode has been enabled'
        ui.rcmetUI()

    #rcmet_cordexAF()
