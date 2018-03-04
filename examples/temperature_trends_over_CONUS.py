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
    temperature_trends_over_CONUS.py

    Use OCW to plot the temperature trends over CONUS using the nClimDiv reference data.

    In this example:

    1. Load the local file nClimDiv/nClimDiv_tave_1895-2005.nc into OCW Dataset Objects.
    *** Note *** It is assume this file exists locally in a subdirectory nClimDiv located
    *** Note *** The files can be downloaded from :
    https://rcmes.jpl.nasa.gov/RCMES_Turtorial_data/NCA-CMIP_examples.tar.gz
    *** Note *** Additional information about the file content can be found here:
    https://rcmes.jpl.nasa.gov/content/nca-cmip-analysis-using-rcmes
    in the same directory as the example.
    2. Load the CMIP5 simulations into a list of OCW Dataset Objects.
    3. Spatially subset the observed dataset into state and regional boundaries.
    4. Temporally subset the observed and model datasets.
    5. Calculate and plot the temperature trend for each region.

    OCW modules demonstrated:

    1. datasource/local
    2. dataset
    3. dataset_processor
    4. plotter
    5. utlis

"""
from __future__ import print_function

import datetime

import numpy as np

import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.plotter as plotter
import ocw.utils as utils
from ocw.dataset import Bounds as Bounds

# nClimGrid observation file
file_obs = 'nClimGrid/nClimGrid_tave_1895-2005.nc'

# CMIP5 simulations
model_file_path = 'CMIP5_historical'
dataset_name = ['BNU-ESM', 'CanESM2', 'CNRM-CM5', 'CSIRO-Mk3', 'GISS-E2-H', 'HadCM3', 'inmcm4',
                'MIROC-ESM', 'MPI-ESM-LR', 'NorESM1-M']
nmodel = len(dataset_name)  # number of CMIP5 simulations

# temporal boundary
start_date = datetime.datetime(1979, 12, 1)
end_date = datetime.datetime(2005, 8, 31)

nyear = 26

month_start = 6  # June
month_end = 8   # August

regions = []
regions.append(['WA', 'OR', 'ID'])
regions.append(['CA', 'NV', 'AZ', 'NM', 'UT', 'CO'])
regions.append(['MT', 'WY', 'ND', 'SD', 'NE'])
regions.append(['KS', 'TX', 'OK'])
regions.append(['MN', 'IA', 'MO', 'WI', 'IL', 'IN', 'MI', 'OH'])
regions.append(['ME', 'VT', 'NH', 'MA', 'NY', 'CT', 'RI', 'NJ', 'PA', 'WV', 'DE', 'MD'])
regions.append(['KY', 'VA', 'AR', 'AL', 'LA', 'MS', 'FL', 'GA', 'NC', 'SC', 'DC', 'TN'])

plotter.fill_US_states_with_color(regions, 'NCA_seven_regions', colors=True,
                                  region_names=['NW', 'SW', 'NGP', 'SGP', 'MW', 'NE', 'SE'])

n_region = 7  # number of regions

# CONUS regional boundaries
NW_bounds = Bounds(boundary_type='us_states', us_states=regions[0])
SW_bounds = Bounds(boundary_type='us_states', us_states=regions[1])
NGP_bounds = Bounds(boundary_type='us_states', us_states=regions[2])
SGP_bounds = Bounds(boundary_type='us_states', us_states=regions[3])
MW_bounds = Bounds(boundary_type='us_states', us_states=regions[4])
NE_bounds = Bounds(boundary_type='us_states', us_states=regions[5])
SE_bounds = Bounds(boundary_type='us_states', us_states=regions[6])

regional_bounds = [NW_bounds, SW_bounds, NGP_bounds,
                   SGP_bounds, MW_bounds, NE_bounds, SE_bounds]

""" Load nClimGrid file into OCW Dataset """
obs_dataset = local.load_file(file_obs, variable_name='tave')

""" Load CMIP5 simulations into a list of OCW Datasets"""
model_dataset = local.load_multiple_files(file_path=model_file_path, variable_name='tas',
                                          dataset_name=dataset_name, variable_unit='K')

""" Temporal subset of obs_dataset """
obs_dataset_subset = dsp.temporal_slice(obs_dataset, start_time=start_date, end_time=end_date)
obs_dataset_season =\
    dsp.temporal_subset(obs_dataset_subset, month_start, month_end, average_each_year=True)

""" Temporal subset of model_dataset """
model_dataset_subset = [dsp.temporal_slice(dataset, start_time=start_date, end_time=end_date)
                        for dataset in model_dataset]
model_dataset_season = [dsp.temporal_subset(dataset, month_start, month_end, average_each_year=True)
                        for dataset in model_dataset_subset]

""" Spatial subset of obs_dataset and generate time series """
obs_timeseries = np.zeros([nyear, n_region])   # region index 0-6: NW, SW, NGP, SGP, MW, NE, SE
model_timeseries = np.zeros([nmodel, nyear, n_region])

for iregion in np.arange(n_region):
    obs_timeseries[:, iregion] =\
        utils.calc_time_series(dsp.subset(obs_dataset_season, regional_bounds[iregion]))
    for imodel in np.arange(nmodel):
        model_timeseries[imodel, :, iregion] =\
            utils.calc_time_series(dsp.subset(model_dataset_season[imodel],
                                              regional_bounds[iregion]))

year = np.arange(nyear)

regional_trends_obs = np.zeros(n_region)
regional_trends_obs_error = np.zeros(n_region)
regional_trends_model = np.zeros([nmodel, n_region])
regional_trends_model_error = np.zeros([nmodel, n_region])
regional_trends_ens = np.zeros(n_region)
regional_trends_ens_error = np.zeros(n_region)

for iregion in np.arange(n_region):
    regional_trends_obs[iregion], regional_trends_obs_error[iregion] =\
        utils.calculate_temporal_trend_of_time_series(year, obs_timeseries[:, iregion])

    for imodel in np.arange(nmodel):
        regional_trends_model[imodel, iregion], regional_trends_model_error[iregion] = \
            utils.calculate_temporal_trend_of_time_series(year,
                                                          model_timeseries[imodel, :, iregion])
    regional_trends_ens[iregion], regional_trends_ens_error[iregion] =\
        utils.calculate_ensemble_temporal_trends(model_timeseries[:, :, iregion])

# Generate plots

plotter.fill_US_states_with_color(regions, 'nClimGrid_tave_trends_JJA_1980-2005',
                                  values=regional_trends_obs,
                                  region_names=['%.3f' % (10*i) for i in regional_trends_obs])

plotter.fill_US_states_with_color(regions, 'CMIP5_ENS_tave_trends_JJA_1980-2005',
                                  values=regional_trends_ens,
                                  region_names=['%.3f' % (10*i) for i in regional_trends_ens])

bias_ens = regional_trends_ens - regional_trends_obs
plotter.fill_US_states_with_color(regions,
                                  'CMIP5_ENS_tave_trends_bias_from_nClimGrid_JJA_1980-2005',
                                  values=bias_ens,
                                  region_names=['%.3f' % (10*i) for i in bias_ens])

obs_data = np.vstack([regional_trends_obs, regional_trends_obs_error])
ens_data = np.vstack([regional_trends_ens, regional_trends_ens_error])

plotter.draw_plot_to_compare_trends(obs_data, ens_data, regional_trends_model,
                                    fname='Trends_comparison_btn_CMIP5_and_nClimGrid',
                                    data_labels=['NW', 'SW', 'NGP', 'SGP', 'MW', 'NE', 'SE'],
                                    xlabel='NCA regions', ylabel='tas trend [K/year]')
