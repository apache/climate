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
    time_series_with_regions.py

    Use OCW to download and plot (time series) three local datasets against a reference dataset.

    In this example:

    1. Download three netCDF files from a local site.
        AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc
        AFRICA_ICTP-REGCM3_CTL_ERAINT_MM_50km-rg_1989-2008_pr.nc
        AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc
    2. Load the local files into OCW dataset objects.
    3. Interface with the Regional Climate Model Evalutaion Database (https://rcmes.jpl.nasa.gov/)
       to load the CRU3.1 Daily Precipitation dataset (https://rcmes.jpl.nasa.gov/content/cru31).
    4. Process each dataset to the same same shape.
        a.) Restrict the datasets re: geographic and time boundaries.
        b.) Convert the dataset water flux to common units.
        c.) Normalize the dataset date / times to monthly.
        d.) Spatially regrid each dataset.
    5.  Calculate the mean monthly value for each dataset.
    6.  Separate each dataset into 13 subregions.
    7.  Create a time series for each dataset in each subregion.

    OCW modules demonstrated:

    1. datasource/local
    2. datasource/rcmed
    3. dataset
    4. dataset_processor
    5. plotter

"""
from __future__ import print_function

import datetime
import ssl
import sys
from calendar import monthrange
from os import path

import numpy as np

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.dataset_processor as dsp
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

LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START = datetime.datetime(2000, 1, 1)
END = datetime.datetime(2007, 12, 31)

EVAL_BOUNDS = Bounds(lat_min=LAT_MIN, lat_max=LAT_MAX,
                     lon_min=LON_MIN, lon_max=LON_MAX, start=START, end=END)

varName = 'pr'
gridLonStep = 0.44
gridLatStep = 0.44

# needed vars for the script
target_datasets = []
tSeries = []
results = []
labels = []  # could just as easily b the names for each subregion
region_counter = 0

# Download necessary NetCDF file if not present
if not path.exists(FILE_1):
    print('Downloading %s' % (FILE_LEADER + FILE_1))
    urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if not path.exists(FILE_2):
    print('Downloading %s' % (FILE_LEADER + FILE_2))
    urlretrieve(FILE_LEADER + FILE_2, FILE_2)

if not path.exists(FILE_3):
    print('Downloading %s' % (FILE_LEADER + FILE_3))
    urlretrieve(FILE_LEADER + FILE_3, FILE_3)

# Step 1: Load Local NetCDF File into OCW Dataset Objects and store in list
target_datasets.append(local.load_file(FILE_1, varName, name='KNMI'))
target_datasets.append(local.load_file(FILE_2, varName, name='REGCM'))
target_datasets.append(local.load_file(FILE_3, varName, name='UCT'))

# Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module
print('Working with the rcmed interface to get CRU3.1 Daily Precipitation')
# the dataset_id and the parameter id were determined from
# https://rcmes.jpl.nasa.gov/content/data-rcmes-database
CRU31 = rcmed.parameter_dataset(
    10, 37, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, START, END)

# Step 3: Processing datasets so they are the same shape
print('Processing datasets so they are the same shape')
CRU31 = dsp.water_flux_unit_conversion(CRU31)
CRU31 = dsp.normalize_dataset_datetimes(CRU31, 'monthly')

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.subset(target_datasets[member], EVAL_BOUNDS)
    target_datasets[member] = dsp.water_flux_unit_conversion(target_datasets[member])
    target_datasets[member] = dsp.normalize_dataset_datetimes(
        target_datasets[member], 'monthly')

print('... spatial regridding')
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)
CRU31 = dsp.spatial_regrid(CRU31, new_lats, new_lons)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] =\
        dsp.spatial_regrid(target_datasets[member], new_lats, new_lons)

# Find climatology monthly for obs and models.
CRU31.values, CRU31.times = utils.calc_climatology_monthly(CRU31)
# Shift the day of the month to the end of the month as matplotlib does not handle
# the xticks elegantly when the first date is the epoch and tries to determine
# the start of the xticks based on a value < 1.
for index, item in enumerate(CRU31.times):
    CRU31.times[index] = \
        datetime.date(item.year, item.month, monthrange(item.year, item.month)[1])

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member].values, target_datasets[member].times = \
        utils.calc_climatology_monthly(target_datasets[member])

# make the model ensemble
target_datasets_ensemble = dsp.ensemble(target_datasets)
target_datasets_ensemble.name = 'ENS'

# append to the target_datasets for final analysis
target_datasets.append(target_datasets_ensemble)

# Step 4: Subregion stuff
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
    Bounds(lat_min=33.0, lat_max=40.0, lon_min=25.0, lon_max=35.0)]

region_list = [['R' + str(i + 1)] for i in range(13)]

for regions in region_list:
    firstTime = True
    subset_name = regions[0] + '_CRU31'
    labels.append(subset_name)
    subset = dsp.subset(CRU31, list_of_regions[region_counter], subset_name)
    tSeries = utils.calc_time_series(subset)
    results.append(tSeries)
    tSeries = []
    firstTime = False
    for member, each_target_dataset in enumerate(target_datasets):
        subset_name = regions[0] + '_' + target_datasets[member].name
        labels.append(subset_name)
        subset = dsp.subset(target_datasets[member],
                            list_of_regions[region_counter],
                            subset_name)
        tSeries = utils.calc_time_series(subset)
        results.append(tSeries)
        tSeries = []

    plotter.draw_time_series(np.array(results), CRU31.times, labels, regions[0],
                             label_month=True, ptitle=regions[0], fmt='png')
    results = []
    tSeries = []
    labels = []
    region_counter += 1
