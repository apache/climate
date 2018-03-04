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
    subregions_rectangular_boundaries.py

    Use OCW to define a set a sub regions and draw the sub regions.

    In this example:

    1. Subset the data set (lat / lon / start date / end date).
    2. Draw each sub region.

    OCW modules demonstrated:

    1. dataset (Bounds)
    2. plotter

"""
from __future__ import print_function

import datetime

import numpy as np

import ocw.plotter as plotter
from ocw.dataset import Bounds

OUTPUT_PLOT = "subregions"

# Spatial and temporal configurations
LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START_SUB = datetime.datetime(2000, 1, 1)
END_SUB = datetime.datetime(2007, 12, 31)

# regridding parameters
gridLonStep = 0.5
gridLatStep = 0.5

# Regrid
print("... regrid")
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)

list_of_regions = [
    Bounds(lat_min=-10.0, lat_max=0.0, lon_min=29.0, lon_max=36.5, start=START_SUB, end=END_SUB),
    Bounds(lat_min=0.0, lat_max=10.0, lon_min=29.0, lon_max=37.5, start=START_SUB, end=END_SUB),
    Bounds(lat_min=10.0, lat_max=20.0, lon_min=25.0, lon_max=32.5, start=START_SUB, end=END_SUB),
    Bounds(lat_min=20.0, lat_max=33.0, lon_min=25.0, lon_max=32.5, start=START_SUB, end=END_SUB),
    Bounds(lat_min=-19.3, lat_max=-10.2, lon_min=12.0, lon_max=20.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=15.0, lat_max=30.0, lon_min=15.0, lon_max=25.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=-10.0, lat_max=10.0, lon_min=7.3, lon_max=15.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=-10.9, lat_max=10.0, lon_min=5.0, lon_max=7.3, start=START_SUB, end=END_SUB),
    Bounds(lat_min=33.9, lat_max=40.0, lon_min=6.9, lon_max=15.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=10.0, lat_max=25.0, lon_min=0.0, lon_max=10.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=10.0, lat_max=25.0, lon_min=-10.0, lon_max=0.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=30.0, lat_max=40.0, lon_min=-15.0, lon_max=0.0, start=START_SUB, end=END_SUB),
    Bounds(lat_min=33.0, lat_max=40.0, lon_min=25.0, lon_max=35.0, start=START_SUB, end=END_SUB)]

# for plotting the subregions
plotter.draw_subregions(list_of_regions, new_lats,
                        new_lons, OUTPUT_PLOT, fmt='png')
