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

import os
import sys
import ssl
import yaml
import operator
from glob import glob
from getpass import getpass
import numpy as np
import ocw.utils as utils
from ocw.dataset import Bounds
from ocw.dataset_loader import DatasetLoader
from metrics_and_plots import *

def load_datasets_from_config(*loader_options, **kwargs):
    '''
    Generic dataset loading function.
    '''
    for opt in loader_options:
        loader_name = opt['loader_name']
        if loader_name == 'ESGF':
            if password is None:
                username=raw_input('Enter your ESGF OpenID:\n')
                password=getpass(prompt='Enter your ESGF password:\n')

            opt['username'] = username
            opt['password'] = password
        elif loader_name == 'rcmed':
            opt['min_lat'] = kwargs['min_lat']
            opt['max_lat'] = kwargs['max_lat']
            opt['min_lon'] = kwargs['min_lon']
            opt['max_lon'] = kwargs['max_lon']
            opt['start_time'] = kwargs['start_time']
            opt['end_time'] = kwargs['end_time']

        loader = DatasetLoader(*loader_options)
        loader.load_datasets()
        return loader.datasets

if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context

config_file = str(sys.argv[1])

print 'Reading the configuration file ', config_file
config = yaml.load(open(config_file))
time_info = config['time']
temporal_resolution = time_info['temporal_resolution']

# Read time info
start_time = datetime.strptime(time_info['start_time'].strftime('%Y%m%d'),'%Y%m%d')
end_time = datetime.strptime(time_info['end_time'].strftime('%Y%m%d'),'%Y%m%d')

# Read space info
space_info = config['space']
min_lat = space_info['min_lat']
max_lat = space_info['max_lat']
min_lon = space_info['min_lon']
max_lon = space_info['max_lon']
kwargs = {'min_lat': min_lat, 'max_lat': max_lat, 'min_lon': min_lon,
          'max_lon': max_lon, 'start_time': start_time, 'end_time': end_time}

# Get the dataset loader options
obs_data_info = config['datasets']['reference']
model_data_info = config['datasets']['targets']

# Extract info we don't want to put into the loader config
# Multiplying Factor to scale obs by
multiplying_factor = np.ones(nobs)
for i, info in enumerate(obs_data_info):
    if 'multiplying_factor' in info:
        multiplying_factor[i] = info.pop('multiplying_factor')

# GCM Boundary Check for Regridding
boundary_check = np.ones(nmodels, dtype='bool')
for i, info in enumerate(model_data_info):
    if 'boundary_check' in info:
        boundary_check[i] = info.pop('boundary_check')

""" Step 1: Load the observation data """
print 'Loading observation datasets:\n',obs_data_info
obs_datasets = load_datasets_from_config(*obs_data_info, **kwargs)
obs_names = [dataset.name for dataset in obs_datasets]
for i, dataset in enumerate(obs_datasets):
    if temporal_resolution == 'daily' or temporal_resolution == 'monthly':
        obs_datasets[i] = dsp.normalize_dataset_datetimes(obs_dataset,
                                                          temporal_resolution)

    if multiplying_factor[i] != 1:
        obs_dataset.values *= multiplying_factor[i]

""" Step 2: Load model NetCDF Files into OCW Dataset Objects """
model_datasets = load_datasets_from_config(*model_data_info, **kwargs)
model_names = [dataset.name for dataset in model_datasets]
if temporal_resolution == 'daily' or temporal_resolution == 'monthly':
    for i, dataset in enumerate(model_datasets):
        model_datasets[i] = dsp.normalize_dataset_datetimes(dataset,
                                                            temporal_resolution)

""" Step 3: Subset the data for temporal and spatial domain """
# Create a Bounds object to use for subsetting
if time_info['maximum_overlap_period']:
    start_time, end_time = utils.get_temporal_overlap([obs_dataset]+model_datasets)
    print 'Maximum overlap period'
    print 'start_time:', start_time
    print 'end_time:', end_time

if temporal_resolution == 'monthly' and end_time.day !=1:
    end_time = end_time.replace(day=1)

for i, dataset in enumerate(obs_datasets):
    min_lat = np.max([min_lat, obs_dataset.lats.min()])
    max_lat = np.min([max_lat, obs_dataset.lats.max()])
    min_lon = np.max([min_lon, obs_dataset.lons.min()])
    max_lon = np.min([max_lon, obs_dataset.lons.max()])

bounds = Bounds(lat_min=min_lat,
                lat_max=max_lat,
                lon_min=min_lon,
                lon_max=max_lon,
                start=start_time,
                end=end_time)

for i, dataset in enumerate(obs_datasets):
    obs_datasets[i] = dsp.subset(dataset, bounds)
    if dataset.temporal_resolution() != temporal_resolution:
        obs_datasets[i] = dsp.temporal_rebin(dataset, temporal_resolution)

for i, dataset in enumerate(model_datasets):
    model_datasets[i] = dsp.subset(dataset, bounds)
    if dataset.temporal_resolution() != temporal_resolution:
        model_datasets[i] = dsp.temporal_rebin(dataset, temporal_resolution)

# Temporally subset both observation and model datasets
# for the user specified season
month_start = time_info['month_start']
month_end = time_info['month_end']
average_each_year = time_info['average_each_year']

# TODO: Fully support multiple observation / reference datasets.
# For now we will only use the first reference dataset listed in the config file
obs_dataset = obs_datasets[0]
obs_name = obs_names[0]
obs_dataset = dsp.temporal_subset(obs_dataset,month_start, month_end,average_each_year)
for i, dataset in enumerate(model_datasets):
    model_datasets[i] = dsp.temporal_subset(dataset, month_start, month_end,
                                            average_each_year)

# generate grid points for regridding
if config['regrid']['regrid_on_reference']:
    new_lat = obs_dataset.lats
    new_lon = obs_dataset.lons
else:
    delta_lat = config['regrid']['regrid_dlat']
    delta_lon = config['regrid']['regrid_dlon']
    nlat = (max_lat - min_lat)/delta_lat+1
    nlon = (max_lon - min_lon)/delta_lon+1
    new_lat = np.linspace(min_lat, max_lat, nlat)
    new_lon = np.linspace(min_lon, max_lon, nlon)

print 'Dataset loading completed'
print 'Observation data:', obs_name
print 'Number of model datasets:',nmodel
for model_name in model_names:
    print model_name

""" Step 4: Spatial regriding of the reference datasets """
print 'Regridding datasets: ', config['regrid']
if not config['regrid']['regrid_on_reference']:
    obs_dataset = dsp.spatial_regrid(obs_dataset, new_lat, new_lon)
    print 'Reference dataset has been regridded'
for i, dataset in enumerate(model_datasets):
    model_datasets[i] = dsp.spatial_regrid(dataset, new_lat, new_lon,
                                           boundary_check=boundary_check[i])
    print model_names[i]+' has been regridded'
print 'Propagating missing data information'
obs_dataset = dsp.mask_missing_data([obs_dataset]+model_datasets)[0]
model_datasets = dsp.mask_missing_data([obs_dataset]+model_datasets)[1:]

""" Step 5: Checking and converting variable units """
print 'Checking and converting variable units'
obs_dataset = dsp.variable_unit_conversion(obs_dataset)
for idata,dataset in enumerate(model_datasets):
    model_datasets[idata] = dsp.variable_unit_conversion(dataset)


print 'Generating multi-model ensemble'
if len(model_datasets) >= 2.:
    model_datasets.append(dsp.ensemble(model_datasets))
    model_names.append('ENS')

""" Step 6: Generate subregion average and standard deviation """
if config['use_subregions']:
    # sort the subregion by region names and make a list
    subregions= sorted(config['subregions'].items(),key=operator.itemgetter(0))

    # number of subregions
    nsubregion = len(subregions)

    print ('Calculating spatial averages and standard deviations of ',
        str(nsubregion),' subregions')

    obs_subregion_mean, obs_subregion_std, subregion_array = (
        utils.calc_subregion_area_mean_and_std([obs_dataset], subregions))
    model_subregion_mean, model_subregion_std, subregion_array = (
        utils.calc_subregion_area_mean_and_std(model_datasets, subregions))

""" Step 7: Write a netCDF file """
workdir = config['workdir']
if workdir[-1] != '/':
    workdir = workdir+'/'
print 'Writing a netcdf file: ',workdir+config['output_netcdf_filename']
if not os.path.exists(workdir):
    os.system("mkdir -p "+workdir)

if config['use_subregions']:
    dsp.write_netcdf_multiple_datasets_with_subregions(
        obs_dataset, obs_name, model_datasets, model_names,
        path=workdir+config['output_netcdf_filename'],
        subregions=subregions, subregion_array=subregion_array,
        obs_subregion_mean=obs_subregion_mean,
        obs_subregion_std=obs_subregion_std,
        model_subregion_mean=model_subregion_mean,
        model_subregion_std=model_subregion_std)
else:
    dsp.write_netcdf_multiple_datasets_with_subregions(
                                obs_dataset, obs_name, model_datasets,
                                model_names,
                                path=workdir+config['output_netcdf_filename'])

""" Step 8: Calculate metrics and draw plots """
nmetrics = config['number_of_metrics_and_plots']
if config['use_subregions']:
    Map_plot_subregion(subregions, obs_dataset, workdir)

if nmetrics > 0:
    print 'Calculating metrics and generating plots'
    for imetric in np.arange(nmetrics)+1:
        metrics_name = config['metrics'+'%1d' %imetric]
        plot_info = config['plots'+'%1d' %imetric]
        file_name = workdir+plot_info['file_name']

        print 'metrics '+str(imetric)+'/'+str(nmetrics)+': ', metrics_name
        if metrics_name == 'Map_plot_bias_of_multiyear_climatology':
            row, column = plot_info['subplots_array']
            if 'map_projection' in plot_info.keys():
                Map_plot_bias_of_multiyear_climatology(
                    obs_dataset, obs_name, model_datasets, model_names,
                    file_name, row, column,
                    map_projection=plot_info['map_projection'])
            else:
                Map_plot_bias_of_multiyear_climatology(
                    obs_dataset, obs_name, model_datasets, model_names,
                    file_name, row, column)
        elif metrics_name == 'Taylor_diagram_spatial_pattern_of_multiyear_climatology':
            Taylor_diagram_spatial_pattern_of_multiyear_climatology(
                obs_dataset, obs_name, model_datasets, model_names,
                file_name)
        elif config['use_subregions']:
            if (metrics_name == 'Timeseries_plot_subregion_interannual_variability'
                and average_each_year):
                row, column = plot_info['subplots_array']
                Time_series_subregion(
                    obs_subregion_mean, obs_name, model_subregion_mean,
                    model_names, False, file_name, row, column,
                    x_tick=['Y'+str(i+1)
                            for i in np.arange(model_subregion_mean.shape[1])])

            if (metrics_name == 'Timeseries_plot_subregion_annual_cycle'
                and not average_each_year and month_start==1 and month_end==12):
                row, column = plot_info['subplots_array']
                Time_series_subregion(
                    obs_subregion_mean, obs_name,
                    model_subregion_mean, model_names, True,
                    file_name, row, column,
                    x_tick=['J','F','M','A','M','J','J','A','S','O','N','D'])

            if (metrics_name == 'Portrait_diagram_subregion_interannual_variability'
                and average_each_year):
                Portrait_diagram_subregion(obs_subregion_mean, obs_name,
                                           model_subregion_mean, model_names,
                                           False, file_name)

            if (metrics_name == 'Portrait_diagram_subregion_annual_cycle'
                and not average_each_year and month_start==1 and month_end==12):
                Portrait_diagram_subregion(obs_subregion_mean, obs_name,
                                           model_subregion_mean, model_names,
                                           True, file_name)
        else:
            print 'please check the currently supported metrics'
