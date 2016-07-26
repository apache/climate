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
import yaml
import os
import sys
import xlwt

import numpy as np
import numpy.ma as ma

import ocw.data_source.local as local
import ocw.dataset as ds
import ocw.dataset_processor as dsp
import ocw.statistical_downscaling as down
import ocw.plotter as plotter

import ssl

def spatial_aggregation(target_dataset, lon_min, lon_max, lat_min, lat_max):
    """ Spatially subset a dataset within the given longitude and latitude boundaryd_lon-grid_space, grid_lon+grid_space
    :param target_dataset: Dataset object that needs spatial subsetting
    :type target_dataset: Open Climate Workbench Dataset Object
    :param lon_min: minimum longitude (western boundary)
    :type lon_min: float
    :param lon_max: maximum longitude (eastern boundary)
    :type lon_min: float
    :param lat_min: minimum latitude (southern boundary) 
    :type lat_min: float
    :param lat_min: maximum latitude (northern boundary) 
    :type lat_min: float
    :returns: A new spatially subset Dataset
    :rtype: Open Climate Workbench Dataset Object
    """

    if target_dataset.lons.ndim == 1 and target_dataset.lats.ndim == 1:
        new_lon, new_lat = np.meshgrid(target_dataset.lons, target_dataset.lats)
    elif target_dataset.lons.ndim == 2 and target_dataset.lats.ndim == 2:
        new_lon = target_datasets.lons
        new_lat = target_datasets.lats
 
    y_index, x_index = np.where((new_lon >= lon_min) & (new_lon <= lon_max) & (new_lat >= lat_min) & (new_lat <= lat_max))[0:2]

    #new_dataset = ds.Dataset(target_dataset.lats[y_index.min():y_index.max()+1],
    #                         target_dataset.lons[x_index.min():x_index.max()+1],
    #                         target_dataset.times,
    #                         target_dataset.values[:,y_index.min():y_index.max()+1,x_index.min():x_index.max()+1],
    #                         target_dataset.variable,
    #                         target_dataset.name) 
    return target_dataset.values[:,y_index.min():y_index.max()+1,x_index.min():x_index.max()+1]

def extract_data_at_nearest_grid_point(target_dataset, longitude, latitude):
    """ Spatially subset a dataset within the given longitude and latitude boundaryd_lon-grid_space, grid_lon+grid_space
    :param target_dataset: Dataset object that needs spatial subsetting
    :type target_dataset: Open Climate Workbench Dataset Object
    :type longitude: float
    :param longitude: longitude
    :type latitude: float
    :param latitude: latitude 
    :returns: A new spatially subset Dataset
    :rtype: Open Climate Workbench Dataset Object
    """

    if target_dataset.lons.ndim == 1 and target_dataset.lats.ndim == 1:
        new_lon, new_lat = np.meshgrid(target_dataset.lons, target_dataset.lats)
    elif target_dataset.lons.ndim == 2 and target_dataset.lats.ndim == 2:
        new_lon = target_datasets.lons
        new_lat = target_datasets.lats
    distance = (new_lon - longitude)**2. + (new_lat - latitude)**2.
    y_index, x_index = np.where(distance == np.min(distance))[0:2]

    return target_dataset.values[:,y_index[0], x_index[0]]

if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context

config_file = str(sys.argv[1])

print 'Reading the configuration file ', config_file

config = yaml.load(open(config_file))

case_name = config['case_name']

downscale_option_names = [' ','delta_addition','delta_correction','quantile_mapping','asynchronous_regression']
DOWNSCALE_OPTION = config['downscaling_option']

location = config['location']
grid_lat = location['grid_lat']
grid_lon = location['grid_lon']

month_index = config['month_index']
month_start = month_index[0]
month_end = month_index[-1]    

ref_info = config['reference']
model_info = config['model']

# Filename for the output data/plot (without file extension)
OUTPUT = "%s_%s_%s_%s_%s" %(location['name'], ref_info['variable'], model_info['data_name'], ref_info['data_name'],model_info['future']['scenario_name'])

print("Processing "+ ref_info['data_name'] + "  data")
""" Step 1: Load Local NetCDF Files into OCW Dataset Objects """

print("Loading %s into an OCW Dataset Object" % (ref_info['path'],))
ref_dataset = local.load_file(ref_info['path'], ref_info['variable'])
print(ref_info['data_name'] +" values shape: (times, lats, lons) - %s \n" % (ref_dataset.values.shape,))

print("Loading %s into an OCW Dataset Object" % (model_info['present']['path'],))
model_dataset_present = local.load_file(model_info['present']['path'], model_info['variable'])
print(model_info['data_name'] +" values shape: (times, lats, lons) - %s \n" % (model_dataset_present.values.shape,))
dy = model_dataset_present.spatial_resolution()[0]
dx = model_dataset_present.spatial_resolution()[1]

model_dataset_future = local.load_file(model_info['future']['path'], model_info['variable'])
print(model_info['future']['scenario_name']+':'+model_info['data_name'] +" values shape: (times, lats, lons) - %s \n" % (model_dataset_future.values.shape,))

""" Step 2: Temporal subsetting """
print("Temporal subsetting for the selected month(s)")
ref_temporal_subset = dsp.temporal_subset(ref_dataset, month_start, month_end)
model_temporal_subset_present = dsp.temporal_subset(model_dataset_present, month_start, month_end)
model_temporal_subset_future = dsp.temporal_subset(model_dataset_future, month_start, month_end)

""" Step 3: Spatial aggregation of observational data into the model grid """
print("Spatial aggregation of observational data near latitude %0.2f and longitude %0.2f " % (grid_lat, grid_lon))
# There are two options to aggregate observational data near a model grid point
#ref_subset = spatial_aggregation(ref_temporal_subset, grid_lon-0.5*dx, grid_lon+0.5*dx, grid_lat-0.5*dy, grid_lat+0.5*dy)
#model_subset_present = spatial_aggregation(model_temporal_subset_present, grid_lon-0.5*dx, grid_lon+0.5*dx, grid_lat-0.5*dy, grid_lat+0.5*dy)
#model_subset_future = spatial_aggregation(model_temporal_subset_future, grid_lon-0.5*dx, grid_lon+0.5*dx, grid_lat-0.5*dy, grid_lat+0.5*dy)
ref_subset = extract_data_at_nearest_grid_point(ref_temporal_subset, grid_lon, grid_lat)
model_subset_present = extract_data_at_nearest_grid_point(model_temporal_subset_present, grid_lon, grid_lat)
model_subset_future = extract_data_at_nearest_grid_point(model_temporal_subset_future, grid_lon, grid_lat)


""" Step 4:  Create a statistical downscaling object and downscaling model output """
# You can add other methods
print("Creating a statistical downscaling object")

downscale = down.Downscaling(ref_subset, model_subset_present, model_subset_future)

print(downscale_option_names[DOWNSCALE_OPTION]+": Downscaling model output")

if DOWNSCALE_OPTION == 1:
    downscaled_model_present, downscaled_model_future = downscale.Delta_addition()
elif DOWNSCALE_OPTION == 2:
    downscaled_model_present, downscaled_model_future = downscale.Delta_correction()
elif DOWNSCALE_OPTION == 3:
    downscaled_model_present, downscaled_model_future = downscale.Quantile_mapping()
elif DOWNSCALE_OPTION == 4:
    downscaled_model_present, downscaled_model_future = downscale.Asynchronous_regression()
else:
    sys.exit("DOWNSCALE_OPTION must be an integer between 1 and 4")


""" Step 5: Create plots and spreadsheet """
print("Plotting results")
if not os.path.exists(case_name):
    os.system("mkdir "+case_name)
os.chdir(os.getcwd()+"/"+case_name)

plotter.draw_marker_on_map(grid_lat, grid_lon, fname='downscaling_location', location_name=config['location']['name'])

plotter.draw_histogram([ref_subset.ravel(), model_subset_present.ravel(), model_subset_future.ravel()], 
                       data_names = [ref_info['data_name'], model_info['data_name'], model_info['future']['scenario_name']],
                       fname=OUTPUT+'_original')
                        
plotter.draw_histogram([ref_subset.ravel(), downscaled_model_present, downscaled_model_future], 
                       data_names = [ref_info['data_name'], model_info['data_name'], model_info['future']['scenario_name']],
                       fname=OUTPUT+'_downscaled_using_'+downscale_option_names[DOWNSCALE_OPTION])

print("Generating spreadsheet")

workbook = xlwt.Workbook()
sheet = workbook.add_sheet(downscale_option_names[config['downscaling_option']])

sheet.write(0, 0, config['location']['name'])
sheet.write(0, 2, 'longitude')
sheet.write(0, 4, 'latitude')
sheet.write(0, 6, 'month')


sheet.write(0, 3, grid_lon)
sheet.write(0, 5, grid_lat)



for imonth,month in enumerate(month_index):
    sheet.write(0, 7+imonth, month)

sheet.write(3, 1, 'observation')
sheet.write(4, 1, ref_info['data_name'])
for idata, data in enumerate(ref_subset.ravel()[~ref_subset.ravel().mask]):
    sheet.write(5+idata,1,data.item())

sheet.write(3, 2, 'original')
sheet.write(4, 2, model_info['data_name'])
for idata, data in enumerate(model_subset_present.ravel()):
    sheet.write(5+idata,2,data.item())

sheet.write(3, 3, 'original')
sheet.write(4, 3, model_info['future']['scenario_name'])
for idata, data in enumerate(model_subset_future.ravel()):
    sheet.write(5+idata,3,data.item())

sheet.write(3, 4, 'downscaled')
sheet.write(4, 4, model_info['data_name'])
for idata, data in enumerate(downscaled_model_present):
    sheet.write(5+idata,4,data.item())

sheet.write(3, 5, 'downscaled')
sheet.write(4, 5, model_info['future']['scenario_name'])
for idata, data in enumerate(downscaled_model_future):
    sheet.write(5+idata,5,data.item())

workbook.save(OUTPUT+'.xls')

