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

import datetime
from os import path
import urllib

import numpy as np

import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.utils as utils

# File URL leader
FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
# Two Local Model Files 
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = "wrf_bias_compared_to_knmi"

FILE_1_PATH = path.join('/tmp', FILE_1)
FILE_2_PATH = path.join('/tmp', FILE_2)

if not path.exists(FILE_1_PATH):
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1_PATH)
if not path.exists(FILE_2_PATH):
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2_PATH)

""" Step 1: Load Local NetCDF Files into OCW Dataset Objects """
print("Loading %s into an OCW Dataset Object" % (FILE_1_PATH,))
knmi_dataset = local.load_file(FILE_1_PATH, "tasmax")
print("KNMI_Dataset.values shape: (times, lats, lons) - %s \n" % (knmi_dataset.values.shape,))

print("Loading %s into an OCW Dataset Object" % (FILE_2_PATH,))
wrf_dataset = local.load_file(FILE_2_PATH, "tasmax")
print("WRF_Dataset.values shape: (times, lats, lons) - %s \n" % (wrf_dataset.values.shape,))

""" Step 2: Calculate seasonal average """
print("Calculate seasonal average")
knmi_DJF_mean = utils.calc_temporal_mean(dsp.temporal_subset(month_start=12, month_end=2, target_dataset=knmi_dataset))
wrf_DJF_mean = utils.calc_temporal_mean(dsp.temporal_subset(month_start=12, month_end=2, target_dataset=wrf_dataset))
print("Seasonally averaged KNMI_Dataset.values shape: (times, lats, lons) - %s \n" % (knmi_DJF_mean.shape,))
print("Seasonally averaged wrf_Dataset.values shape: (times, lats, lons) - %s \n" % (wrf_DJF_mean.shape,))
knmi_JJA_mean = utils.calc_temporal_mean(dsp.temporal_subset(month_start=6, month_end=8, target_dataset=knmi_dataset))
wrf_JJA_mean = utils.calc_temporal_mean(dsp.temporal_subset(month_start=6, month_end=8, target_dataset=wrf_dataset))

