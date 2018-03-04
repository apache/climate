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

"""
    subregions_portrait_diagram.py

    Use OCW to download, normalize, evaluate and plot (portrait diagram)
    three local datasets against a reference dataset.

    In this example:

    1. Download three netCDF files from a local site.
        AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc
        AFRICA_ICTP-REGCM3_CTL_ERAINT_MM_50km-rg_1989-2008_pr.nc
        AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc
    2. Load the local files into OCW dataset objects.
    3. Interface with the Regional Climate Model Evaluation Database (https://rcmes.jpl.nasa.gov/)
       to load the CRU3.1 Daily Precipitation dataset (https://rcmes.jpl.nasa.gov/content/cru31).
    4. Process each dataset to the same same shape.
        a.) Restrict the datasets re: geographic and time boundaries.
        b.) Convert the dataset water flux to common units.
        c.) Normalize the dataset date / times to monthly.
        d.) Spatially regrid each dataset.
    5.  Calculate the mean annual value for each dataset.
    6.  Separate each dataset into 13 subregions.
    7.  Extract the metrics used for the evaluation and evaluate
        against a reference dataset.
    8.  Create a portrait diagram of the results of the evaluation.

    OCW modules demonstrated:

    1. datasource/local
    2. datasource/rcmed
    3. dataset
    4. dataset_processor
    5. metrics
    6. evaluation
    7. plotter
    8. utils

"""
from __future__ import print_function

import datetime
import ssl
import sys
from os import path

import numpy as np

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.utils as utils
from ocw.dataset import Bounds

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# File URL leader
FILE_LEADER = 'http://zipper.jpl.nasa.gov/dist/'
# Three Local Model Files
FILE_1 = 'AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc'
FILE_2 = 'AFRICA_ICTP-REGCM3_CTL_ERAINT_MM_50km-rg_1989-2008_pr.nc'
FILE_3 = 'AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc'
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = 'portrait_diagram'

# Spatial and temporal configurations
LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START = datetime.datetime(2000, 1, 1)
END = datetime.datetime(2007, 12, 31)
EVAL_BOUNDS = Bounds(lat_min=LAT_MIN, lat_max=LAT_MAX, lon_min=LON_MIN,
                     lon_max=LON_MAX, start=START, end=END)

# variable that we are analyzing
varName = 'pr'

# regridding parameters
gridLonStep = 0.5
gridLatStep = 0.5

# some vars for this evaluation
target_datasets_ensemble = []
target_datasets = []
allNames = []

# Download necessary NetCDF file if not present
if not path.exists(FILE_1):
    urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if not path.exists(FILE_2):
    urlretrieve(FILE_LEADER + FILE_2, FILE_2)

if not path.exists(FILE_3):
    urlretrieve(FILE_LEADER + FILE_3, FILE_3)

# Step 1: Load Local NetCDF File into OCW Dataset Objects and store in list
target_datasets.append(local.load_file(FILE_1, varName, name='KNMI'))
target_datasets.append(local.load_file(FILE_2, varName, name='REGCM'))
target_datasets.append(local.load_file(FILE_3, varName, name='UCT'))

# Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module
print('Working with the rcmed interface to get CRU3.1 Monthly Mean Precipitation')
# the dataset_id and the parameter id were determined from
# https://rcmes.jpl.nasa.gov/content/data-rcmes-database
CRU31 = rcmed.parameter_dataset(
    10, 37, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, START, END)

# Step 3: Processing Datasets so they are the same shape
print('Processing datasets ...')
CRU31 = dsp.normalize_dataset_datetimes(CRU31, 'monthly')
print('... on units')
CRU31 = dsp.water_flux_unit_conversion(CRU31)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.subset(target_datasets[member], EVAL_BOUNDS)
    target_datasets[member] = \
        dsp.water_flux_unit_conversion(target_datasets[member])
    target_datasets[member] = dsp.normalize_dataset_datetimes(
        target_datasets[member], 'monthly')

print('... spatial regridding')
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)
CRU31 = dsp.spatial_regrid(CRU31, new_lats, new_lons)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.spatial_regrid(
        target_datasets[member], new_lats, new_lons)

# find the total annual mean. Note the function exists in util.py as def
# calc_climatology_year(dataset):
_, CRU31.values = utils.calc_climatology_year(CRU31)

for member, each_target_dataset in enumerate(target_datasets):
    _, target_datasets[member].values = \
        utils.calc_climatology_year(target_datasets[member])

# make the model ensemble
target_datasets_ensemble = dsp.ensemble(target_datasets)
target_datasets_ensemble.name = 'ENS'

# append to the target_datasets for final analysis
target_datasets.append(target_datasets_ensemble)

for target in target_datasets:
    allNames.append(target.name)

list_of_regions = [
    Bounds(lat_min=-10.0, lat_max=0.0, lon_min=29.0, lon_max=36.5),
    Bounds(lat_min=0.0, lat_max=10.0, lon_min=29.0, lon_max=37.5),
    Bounds(lat_min=10.0, lat_max=20.0, lon_min=25.0, lon_max=32.5),
    Bounds(lat_min=20.0, lat_max=33.0, lon_min=25.0, lon_max=32.5),
    Bounds(lat_min=-19.3, lat_max=-10.2, lon_min=12.0, lon_max=20.0),
    Bounds(lat_min=15.0, lat_max=30.0, lon_min=15.0, lon_max=25.0),
    Bounds(lat_min=-10.0, lat_max=10.0, lon_min=7.3, lon_max=15.0),
    Bounds(lat_min=-10.9, lat_max=10.0, lon_min=5.0, lon_max=7.3),
    Bounds(lat_min=33.9, lat_max=40.0, lon_min=6.9, lon_max=15.0),
    Bounds(lat_min=10.0, lat_max=25.0, lon_min=0.0, lon_max=10.0),
    Bounds(lat_min=10.0, lat_max=25.0, lon_min=-10.0, lon_max=0.0),
    Bounds(lat_min=30.0, lat_max=40.0, lon_min=-15.0, lon_max=0.0),
    Bounds(lat_min=33.0, lat_max=40.0, lon_min=25.0, lon_max=35.00)]

region_list = ['R' + str(i + 1) for i in range(13)]

# metrics
pattern_correlation = metrics.PatternCorrelation()

# create the Evaluation object
RCMs_to_CRU_evaluation = evaluation.Evaluation(CRU31,  # Reference dataset for the evaluation
                                               # 1 or more target datasets for
                                               # the evaluation
                                               target_datasets,
                                               # 1 or more metrics to use in
                                               # the evaluation
                                               [pattern_correlation],
                                               # list of subregion Bounds
                                               # Objects
                                               list_of_regions)
RCMs_to_CRU_evaluation.run()

new_patcor = np.squeeze(np.array(RCMs_to_CRU_evaluation.results), axis=1)

plotter.draw_portrait_diagram(np.transpose(
    new_patcor), allNames, region_list, fname=OUTPUT_PLOT, fmt='png', cmap='coolwarm_r')
