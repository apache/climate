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

from __future__ import print_function
import os
import sys
import ssl
import yaml
import operator
from datetime import datetime
from glob import glob
from getpass import getpass
import numpy as np
import ocw.utils as utils
import ocw.dataset_processor as dsp
from ocw.dataset import Bounds
from ocw.dataset_loader import DatasetLoader
from metrics_and_plots import *

def load_datasets_from_config(extra_opts, *loader_opts):
    '''
    Generic dataset loading function.
    '''
    for opt in loader_opts:
        loader_name = opt['loader_name']
        if loader_name == 'esgf':
            if extra_opts['password'] is None:
                extra_opts['username'] = raw_input('Enter your ESGF OpenID:\n')
                extra_opts['password'] = getpass(
                                        prompt='Enter your ESGF password:\n')

            opt['esgf_username'] = extra_opts['username']
            opt['esgf_password'] = extra_opts['password']
        elif loader_name == 'rcmed':
            opt['min_lat'] = extra_opts['min_lat']
            opt['max_lat'] = extra_opts['max_lat']
            opt['min_lon'] = extra_opts['min_lon']
            opt['max_lon'] = extra_opts['max_lon']
            opt['start_time'] = extra_opts['start_time']
            opt['end_time'] = extra_opts['end_time']

    loader = DatasetLoader(*loader_opts)
    loader.load_datasets()
    return loader.datasets

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

config_file = str(sys.argv[1])

print('Reading the configuration file {}'.format(config_file))
config = yaml.load(open(config_file))
time_info = config['time']
temporal_resolution = time_info['temporal_resolution']

# Read time info
start_time = datetime.strptime(time_info['start_time'].strftime('%Y%m%d'),'%Y%m%d')
end_time = datetime.strptime(time_info['end_time'].strftime('%Y%m%d'),'%Y%m%d')

# Read space info
space_info = config['space']
if not 'boundary_type' in space_info:
    min_lat = space_info['min_lat']
    max_lat = space_info['max_lat']
    min_lon = space_info['min_lon']
    max_lon = space_info['max_lon']
else:
    min_lat, max_lat, min_lon, max_lon = utils.CORDEX_boundary(space_info['boundary_type'][6:].replace(" ","").lower())

# Additional arguments for the DatasetLoader
extra_opts = {'min_lat': min_lat, 'max_lat': max_lat, 'min_lon': min_lon,
              'max_lon': max_lon, 'start_time': start_time,
              'end_time': end_time, 'username': None, 'password': None}

# Get the dataset loader options
data_info = config['datasets']

# Extract info we don't want to put into the loader config
# Multiplying Factor to scale obs by. Currently only supported for reference
# (first) dataset. We should instead make this a parameter for each
# loader and Dataset objects.
fact = data_info[0].pop('multiplying_factor', 1)
    
""" Step 1: Load the datasets """
print('Loading datasets:\n{}'.format(data_info))
datasets = load_datasets_from_config(extra_opts, *data_info)
multiplying_factor = np.ones(len(datasets))
multiplying_factor[0] = fact
names = [dataset.name for dataset in datasets]
for i, dataset in enumerate(datasets):
    if temporal_resolution == 'daily' or temporal_resolution == 'monthly':
        datasets[i] = dsp.normalize_dataset_datetimes(dataset,
                                                      temporal_resolution)
        if multiplying_factor[i] != 1:
            datasets[i].values *= multiplying_factor[i]

""" Step 2: Subset the data for temporal and spatial domain """
# Create a Bounds object to use for subsetting
if time_info['maximum_overlap_period']:
    start_time, end_time = utils.get_temporal_overlap(datasets)
    print('Maximum overlap period')
    print('start_time: {}'.format(start_time))
    print('end_time: {}'.format(end_time))

if temporal_resolution == 'monthly' and end_time.day !=1:
    end_time = end_time.replace(day=1)

for i, dataset in enumerate(datasets):
    min_lat = np.max([min_lat, dataset.lats.min()])
    max_lat = np.min([max_lat, dataset.lats.max()])
    min_lon = np.max([min_lon, dataset.lons.min()])
    max_lon = np.min([max_lon, dataset.lons.max()])

if not 'boundary_type' in space_info:
    bounds = Bounds(lat_min=min_lat,
                    lat_max=max_lat,
                    lon_min=min_lon,
                    lon_max=max_lon,
                    start=start_time,
                    end=end_time)
else:
    bounds = Bounds(boundary_type=space_info['boundary_type'],
                    start=start_time,
                    end=end_time)

for i, dataset in enumerate(datasets):
    datasets[i] = dsp.subset(dataset, bounds)
    if dataset.temporal_resolution() != temporal_resolution:
        datasets[i] = dsp.temporal_rebin(dataset, temporal_resolution)

# Temporally subset both observation and model datasets
# for the user specified season
month_start = time_info['month_start']
month_end = time_info['month_end']
average_each_year = time_info['average_each_year']

# For now we will treat the first listed dataset as the reference dataset for
# evaluation purposes.
for i, dataset in enumerate(datasets):
    datasets[i] = dsp.temporal_subset(dataset, month_start, month_end,
                                      average_each_year)

reference_dataset = datasets[0]
target_datasets = datasets[1:]
reference_name = names[0]
target_names = names[1:]

# generate grid points for regridding
if config['regrid']['regrid_on_reference']:
    new_lat = reference_dataset.lats
    new_lon = reference_dataset.lons
else:
    delta_lat = config['regrid']['regrid_dlat']
    delta_lon = config['regrid']['regrid_dlon']
    nlat = (max_lat - min_lat)/delta_lat+1
    nlon = (max_lon - min_lon)/delta_lon+1
    new_lat = np.linspace(min_lat, max_lat, nlat)
    new_lon = np.linspace(min_lon, max_lon, nlon)

# Get flag for boundary checking for regridding. By default, this is set to True
# since the main intent of this program is to evaluate RCMs. However, it can be
# used for GCMs in which case it should be set to False to save time.
boundary_check = config['regrid'].get('boundary_check', True)

# number of target datasets (usually models, but can also be obs / reanalysis)
ntarget = len(target_datasets)
print('Dataset loading completed')
print('Reference data: {}'.format(reference_name))
print('Number of target datasets: {}'.format(ntarget))
for target_name in target_names:
    print(target_name)

""" Step 3: Spatial regriding of the datasets """
print('Regridding datasets: {}'.format(config['regrid']))
if not config['regrid']['regrid_on_reference']:
    reference_dataset = dsp.spatial_regrid(reference_dataset, new_lat, new_lon)
    print('Reference dataset has been regridded')
for i, dataset in enumerate(target_datasets):
    target_datasets[i] = dsp.spatial_regrid(dataset, new_lat, new_lon,
                                           boundary_check=boundary_check)
    print('{} has been regridded'.format(target_names[i]))
print('Propagating missing data information')
datasets = dsp.mask_missing_data([reference_dataset]+target_datasets)
reference_dataset = datasets[0]
target_datasets = datasets[1:]

""" Step 4: Checking and converting variable units """
print('Checking and converting variable units')
reference_dataset = dsp.variable_unit_conversion(reference_dataset)
for i, dataset in enumerate(target_datasets):
    target_datasets[i] = dsp.variable_unit_conversion(dataset)

print('Generating multi-model ensemble')
if len(target_datasets) >= 2.:
    target_datasets.append(dsp.ensemble(target_datasets))
    target_names.append('ENS')

""" Step 5: Generate subregion average and standard deviation """
if config['use_subregions']:
    # sort the subregion by region names and make a list
    subregions= sorted(config['subregions'].items(),key=operator.itemgetter(0))

    # number of subregions
    nsubregion = len(subregions)

    print('Calculating spatial averages and standard deviations of {} subregions'
          .format(nsubregion))

    reference_subregion_mean, reference_subregion_std, subregion_array = (
        utils.calc_subregion_area_mean_and_std([reference_dataset], subregions))
    target_subregion_mean, target_subregion_std, subregion_array = (
        utils.calc_subregion_area_mean_and_std(target_datasets, subregions))

""" Step 6: Write a netCDF file """
workdir = config['workdir']
if workdir[-1] != '/':
    workdir = workdir+'/'
print('Writing a netcdf file: ',workdir+config['output_netcdf_filename'])
if not os.path.exists(workdir):
    os.system("mkdir -p "+workdir)

if config['use_subregions']:
    dsp.write_netcdf_multiple_datasets_with_subregions(
        reference_dataset, reference_name, target_datasets, target_names,
        path=workdir+config['output_netcdf_filename'],
        subregions=subregions, subregion_array=subregion_array,
        ref_subregion_mean=reference_subregion_mean,
        ref_subregion_std=reference_subregion_std,
        model_subregion_mean=target_subregion_mean,
        model_subregion_std=target_subregion_std)
else:
    dsp.write_netcdf_multiple_datasets_with_subregions(
                                reference_dataset, reference_name, target_datasets,
                                target_names,
                                path=workdir+config['output_netcdf_filename'])

""" Step 7: Calculate metrics and draw plots """
nmetrics = config['number_of_metrics_and_plots']
if config['use_subregions']:
    Map_plot_subregion(subregions, reference_dataset, workdir)

if nmetrics > 0:
    print('Calculating metrics and generating plots')
    for imetric in np.arange(nmetrics)+1:
        metrics_name = config['metrics'+'%1d' %imetric]
        plot_info = config['plots'+'%1d' %imetric]
        file_name = workdir+plot_info['file_name']

        print('metrics {0}/{1}: {2}'.format(imetric, nmetrics, metrics_name))
        if metrics_name == 'Map_plot_bias_of_multiyear_climatology':
            row, column = plot_info['subplots_array']
            if 'map_projection' in plot_info.keys():
                Map_plot_bias_of_multiyear_climatology(
                    reference_dataset, reference_name, target_datasets, target_names,
                    file_name, row, column,
                    map_projection=plot_info['map_projection'])
            else:
                Map_plot_bias_of_multiyear_climatology(
                    reference_dataset, reference_name, target_datasets, target_names,
                    file_name, row, column)
        elif metrics_name == 'Taylor_diagram_spatial_pattern_of_multiyear_climatology':
            Taylor_diagram_spatial_pattern_of_multiyear_climatology(
                reference_dataset, reference_name, target_datasets, target_names,
                file_name)
        elif config['use_subregions']:
            if (metrics_name == 'Timeseries_plot_subregion_interannual_variability'
                and average_each_year):
                row, column = plot_info['subplots_array']
                Time_series_subregion(
                    reference_subregion_mean, reference_name, target_subregion_mean,
                    target_names, False, file_name, row, column,
                    x_tick=['Y'+str(i+1)
                            for i in np.arange(target_subregion_mean.shape[1])])

            if (metrics_name == 'Timeseries_plot_subregion_annual_cycle'
                and not average_each_year and month_start==1 and month_end==12):
                row, column = plot_info['subplots_array']
                Time_series_subregion(
                    reference_subregion_mean, reference_name,
                    target_subregion_mean, target_names, True,
                    file_name, row, column,
                    x_tick=['J','F','M','A','M','J','J','A','S','O','N','D'])

            if (metrics_name == 'Portrait_diagram_subregion_interannual_variability'
                and average_each_year):
                Portrait_diagram_subregion(reference_subregion_mean, reference_name,
                                           target_subregion_mean, target_names,
                                           False, file_name)

            if (metrics_name == 'Portrait_diagram_subregion_annual_cycle'
                and not average_each_year and month_start==1 and month_end==12):
                Portrait_diagram_subregion(reference_subregion_mean, reference_name,
                                           target_subregion_mean, target_names,
                                           True, file_name)
        else:
            print('please check the currently supported metrics')
