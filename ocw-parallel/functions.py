# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import sys, os, datetime
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse
from datetime import timedelta
import numpy as np

import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter


def loadDataset(urlAndVariable, dir=None):
    '''Load a dataset (variable), returning a Dataset object.'''
    shortName = None
    if len(urlAndVariable) == 3:
        url, variable, shortName = urlAndVariable
    else:
        url, variable = urlAndVariable
    f = retrieveFile(url, dir)
    ds = local.load_file(f, variable)
    if shortName is None or shortName == '':
        shortName = f + '?' + variable
    ds.name = shortName
    shape = ds.values.shape
    if len(shape) == 3:
        coords = '(time, lat, lon)'
    elif len(shape) == 2:
        coords = '(lat, lon)'
    print('loadDataset: File %s has variable %s with shape %s: %s' % (f, variable, coords, shape), file=sys.stderr) 
    return ds

def loadDatasets(urlAndVariables, dir=None):
    return [loadDataset(uv, dir) for uv in urlAndVariables]


def temporalRegrid(dataset, timeRes=timedelta(days=365)):
    '''Temporally rebin a dataset variable to a specified time resolution (timedelta object).'''
    dataset = dsp.temporal_rebin(dataset, timeRes)
    name = dataset.name
    if name is None: name = ''
    print('temporalRebin: Dataset %s has new shape %s' % (name, str(dataset.values.shape)), file=sys.stderr)
    return dataset

def temporalRegrids(datasets, timeRes=timedelta(days=365)):
    '''Temporally rebin dataset variables to a specified time resolution (timedelta object).'''
    return [temporalRegrid(d, timeRes) for d in datasets]


def spatialBounds(dataset): return dataset.spatial_boundaries()

def commonSpatialBounds(datasets):
    '''Compute overlapping (intersection) spatial bounds of many datasets.'''
    bounds = [spatialBounds(ds) for ds in datasets]
    for i, b in enumerate(bounds):
        name = datasets[i].name
        if name is None or name == '': name = str(i)
        print('commonSpatialBounds: Dataset %s has boundaries: lat (%s, %s), lon (%s, %s).' % \
                                (name, b[0], b[1], b[2], b[3]), file=sys.stderr)
    minLat = max([b[0] for b in bounds])
    maxLat = min([b[1] for b in bounds])
    minLon = max([b[2] for b in bounds])
    maxLon = min([b[3] for b in bounds])
    print('commonSpatialBounds: Common boundaries are: lat (%s, %s), lon (%s, %s).' % \
                            (minLat, maxLat, minLon, maxLon), file=sys.stderr)
    return (minLat, maxLat, minLon, maxLon)

def generateLatLonGrid(latGrid, lonGrid):
    '''Generate a uniform lat/lon grid at set resolutions, where latGrid is a tuple of (latMin, latMax, latRes).'''
    minLat, maxLat, latRes = list(map(float, latGrid))
    minLon, maxLon, lonRes = list(map(float, lonGrid))
    lats = np.arange(minLat, maxLat, float(latRes))
    lons = np.arange(minLon, maxLon, float(lonRes))
    return (lats, lons)

def commonLatLonGrid(datasets, latRes, lonRes):
    '''Find common (intersect) lat/lon bounds and construct new grid with specified lat/lon resolutions.'''
    minLat, maxLat, minLon, maxLon = commonSpatialBounds(datasets)
    latGrid = (minLat, maxLat, latRes)
    lonGrid = (minLon, maxLon, lonRes)
    return generateLatLonGrid(latGrid, lonGrid)


def spatialRegrid(dataset, lats, lons):
    '''Spatially regrid dataset variable to a new grid with specified resolution, where lats & lons
are the new coordinate vectors.
    '''
    return dsp.spatial_regrid(dataset, lats, lons)
    
def spatialRegrids(datasets, lats, lons):
    '''Spatially regrid dataset variables to a new grid with specified resolution, where lats & lons
are the new coordinate vectors.
    '''
    return [spatialRegrid(d, lats, lons) for d in datasets]


def lookupMetrics(metricNames,
                  availableMetrics={'Bias': metrics.Bias, 'StdDevRatio': metrics.StdDevRatio,
                                    'PatternCorrelation': metrics.PatternCorrelation}):
    '''Return a list of metric objects given a list of string names.'''
    metrics = []
    for name in metricNames:
        try:
            m = availableMetrics[name]
            metrics.append(m())
        except:
            print('lookupMetrics: Error, No metric named %s' % name, file=sys.stderr)
    return metrics

def computeMetrics(datasets, metricNames=['Bias'], subregions=None):
    '''Compute one or more metrics comparing multiple target datasets to a reference dataset.
This routine assumes that the datasets have already been regridded so that there grid dimensions
are identical.
    '''
    metrics = lookupMetrics(metricNames)
    if len(metrics) != len(metricNames):
        print('computeMetrics: Error, Illegal or misspelled metric name.', file=sys.stderr)
    eval = evaluation.Evaluation(datasets[0], datasets[1:], metrics)
    print('computeMetrics: Evaluating metrics %s . . .' % str(metricNames), file=sys.stderr)
    eval.run()
    return eval.results


def compareVariablesWithMetrics(datasetUrlsAndVarNames,         # URL's pointing to datasets, first one is reference, rest are targets; 
                                                                # each tuple can be (datasetUrl, variableName, shortName), shortName optional
                           metrics,                             # list of metrics to compute (by name)
                           outputName,                          # root name for outputs
                           timeRes=timedelta(days=365),         # time resolution to regrid all variables to
                           latRes=1., lonRes=1.,                # lat/lon resolutions to regrid all variables to
                           subregions=None,                     # list of subregion boundaries
                           dir='./'):                           # directory for outputs, defaults to current working dir
    '''Compare multiple target variables to a reference variable, returning the computed metric(s)
after temporally rebinning to a common time resolution and a common spatial (lat/lon) resolution.
    '''
    datasets = loadDatasets(datasetUrlsAndVarNames, dir)
    
    datasets = temporalRegrids(datasets, timeRes)
    
    newLats, newLons = commonLatLonGrid(datasets, latRes, lonRes)
    datasets = spatialRegrids(datasets, newLats, newLons)

#    datasets = maskMissingValues(datasets, missingValues)
    
    metrics = computeMetrics(datasets, metrics, subregions)
    return (newLats, newLons, metrics)


def plotBias(metric, lats, lons, outputName, **config):
    '''Plot the bias of the reference datasets compared to multiple targets.'''
    plotFile = outputName + '.png'
    print(('plotBias: Writing %s' % plotFile))
    plotter.draw_contour_map(metric, lats, lons, outputName, **config)
    return plotFile


# Utilities follow.

def isLocalFile(url):
    '''Check if URL is a local path.'''
    u = urlparse(url)
    if u.scheme == '' or u.scheme == 'file':
        if not path.exists(u.path):
            print('isLocalFile: File at local path does not exist: %s' % u.path, file=sys.stderr)
        return (True, u.path)
    else:
        return (False, u.path)

def retrieveFile(url, dir=None):
    '''Retrieve a file from a URL, or if it is a local path then verify it exists.'''
    if dir is None: dir = './'
    ok, path = isLocalFile(url)
    fn = os.path.split(path)[1]
    outPath = os.path.join(dir, fn)
    if not ok:
        if os.path.exists(outPath):
            print('retrieveFile: Using cached file: %s' % outPath, file=sys.stderr)
        else:
            try:
                print('retrieveFile: Retrieving (URL) %s to %s' % (url, outPath), file=sys.stderr)
                urllib.request.urlretrieve(url, outPath)
            except:
                print('retrieveFile: Cannot retrieve file at URL: %s' % url, file=sys.stderr)
                return None
    return outPath    


# Tests and main follow.

def test1(urlsAndVars, outputName, **config):
    '''Test compareManyWithMetrics routine.'''
    lats, lons, metrics = compareVariablesWithMetrics(urlsAndVars, ['Bias'], outputName, timedelta(days=365), 1, 1)
    print(metrics)
    
    config = {'gridshape': (4, 5),
              'ptitle': 'TASMAX Bias of WRF Compared to KNMI (1989 - 2008)',
              'subtitles': list(range(1989, 2009, 1))}
    plotFile = plotBias(metrics[0][0], lats, lons, outputName, **config)
    return plotFile


def main(args):
    '''Main routine to provide command line capability.'''
    nTest = int(args[0])
    url1 = args[1]
    var1 = args[2]
    outputName = args[3]
    url2 = args[4]
    var2 = args[5]
    urlsAndVars = [(url1, var1),  (url2, var2)]
    if nTest == 1:
        return test1(urlsAndVars, outputName)
    elif nTest == 2:
        return test2(urlsAndVars, outputName)

if __name__ == '__main__':
    print(main(sys.argv[1:]))


# python functions.py 1 "http://zipper.jpl.nasa.gov/dist/AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc" "tasmax" "wrf_bias_compared_to_knmi" "http://zipper.jpl.nasa.gov/dist/AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc" "tasmax"

