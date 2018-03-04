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
    GPM_WRF24_JPDF_comparison.py

    This is an example of calculating the joint probability distribution
    function of rainfall intensity and duration for the Northern Great
    Plains using GPM IMERG data for June/01/2015

    In this example:

    1. Load the GPM and WRF24 datasets with spatial filter.
    2. Load the spatial filter (Bukovsky region mask).
    3. Spatially subset the WRF data.
    4. Analyze the wet spells.
    5. Calculate the joint PDF(JPDF) of spell_duration and peak_rainfall.
    6. Visualize the JPDF.

    OCW modules demonstrated:

    1. datasource/local
    2. dataset
    3. dataset_processor
    4. metrics
    5. plotter

"""
from __future__ import print_function

import numpy as np

import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.metrics as metrics
import ocw.plotter as plotter
from ocw.dataset import Bounds

# Step 1: Load the GPM and WRF24 datasets with spatial filter.

GPM_dataset_filtered = local.load_GPM_IMERG_files_with_spatial_filter(
    file_path='./data/GPM_2015_summer/',
    user_mask_file='Bukovsky_regions.nc',
    mask_variable_name='Bukovsky',
    user_mask_values=[10],
    longitude_name='lon',
    latitude_name='lat')

WRF_dataset = local.load_WRF_2d_files_RAIN(
    file_path='./data/WRF24_2010_summer/',
    filename_pattern=['wrf2dout*'])

# Step 2: Load the spatial filter (Bukovsky region mask).

Bukovsky_mask = Bounds(
    boundary_type='user',
    user_mask_file='Bukovsky_regions.nc',
    mask_variable_name='Bukovsky',
    longitude_name='lon',
    latitude_name='lat')

# Step 3: Spatial subset the WRF data (for Northern Great Plains, user_mask_values=[10]).

WRF_dataset_filtered = \
    dsp.subset(WRF_dataset, Bukovsky_mask, user_mask_values=[10])

# Step 4: Analyze the wet spells.
duration1, peak1, total1 = \
    metrics.wet_spell_analysis(GPM_dataset_filtered, threshold=0.1, nyear=1, dt=0.5)

duration2, peak2, total2 =\
    metrics.wet_spell_analysis(WRF_dataset_filtered.values, threshold=0.1, nyear=1, dt=0.5)

# Step 5: Calculate the joint PDF(JPDF) of spell_duration and peak_rainfall.

histo2d_GPM = \
    metrics.calc_joint_histogram(data_array1=duration1, data_array2=peak1,
                                 bins_for_data1=np.append(np.arange(25)+0.5, [48.5, 120.5]),
                                 bins_for_data2=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10, 20, 30])
histo2d_GPM = histo2d_GPM/np.sum(histo2d_GPM) * 100.

histo2d_WRF =\
    metrics.calc_joint_histogram(data_array1=duration2, data_array2=peak2,
                                 bins_for_data1=np.append(np.arange(25)+0.5, [48.5, 120.5]),
                                 bins_for_data2=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10, 20, 30])

histo2d_WRF = histo2d_WRF/np.sum(histo2d_WRF) * 100.

# Step 6: Visualize the JPDF.


plot_level = np.array([0., 0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 25])
plotter.draw_precipitation_JPDF(plot_data=np.transpose(histo2d_GPM),
                                plot_level=plot_level, title='',
                                x_ticks=[0.5, 4.5, 9.5, 14.5, 19.5, 23.5],
                                x_names=['1', '5', '10', '15', '20', '24'],
                                y_ticks=np.arange(9),
                                y_names=['0.1', '0.2', '0.5', '1.0', '2.0', '5.0', '10', '20', '30'],
                                output_file='GPM_JPDF_example')

plotter.draw_precipitation_JPDF(plot_data=np.transpose(histo2d_WRF),
                                plot_level=plot_level, title='',
                                x_ticks=[0.5, 4.5, 9.5, 14.5, 19.5, 23.5],
                                x_names=['1', '5', '10', '15', '20', '24'],
                                y_ticks=np.arange(9),
                                y_names=['0.1', '0.2', '0.5', '1.0', '2.0', '5.0', '10', '20', '30'],
                                output_file='WRF24_JPDF_example')

overlap = metrics.calc_histogram_overlap(histo2d_GPM, histo2d_WRF)
plot_level = np.array([-21, -3, -1, -0.5, -0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2, 0.5, 1, 3, 21])
cbar_ticks = [-2, -0.5, -0.1, 0.1, 0.5, 2]
cbar_label = [str(i) for i in cbar_ticks]
plotter.draw_precipitation_JPDF(plot_data=np.transpose(histo2d_WRF - histo2d_GPM),
                                plot_level=plot_level, title='overlap %d ' % overlap + r'%',
                                diff_plot=True, x_ticks=[0.5, 4.5, 9.5, 14.5, 19.5, 23.5],
                                x_names=['1', '5', '10', '15', '20', '24'],
                                y_ticks=np.arange(9),
                                y_names=['0.1', '0.2', '0.5', '1.0', '2.0', '5.0', '10', '20', '30'],
                                output_file='GPM_WRF24_JPDF_comparison',
                                cbar_ticks=cbar_ticks, cbar_label=cbar_label)
