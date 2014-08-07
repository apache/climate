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

import curses
import sys
import os
import numpy as np

from netCDF4 import Dataset
from datetime import datetime, timedelta

import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.data_source.rcmed as rcmed
from ocw.dataset import Bounds
from ocw.data_source.local import load_file


def ready_screen(page, note=""):
     ''' Generates page borders, header, footer and notification center.

     :param note: Notification that system returns and will be shown
          at the bottom of page
     :type note: string
     :param page: Name of current page
     :type page: string

     :returns: y and x as location of text on screen
     :rtype: integer
     '''

     screen.clear()
     y, x = screen.getmaxyx()
     screen.border(0)
     screen.addstr(0, x/2-len(TITLE)/2, TITLE)
     screen.addstr(y-1, x/2-len(ORGANIZATION)/2, ORGANIZATION)
     screen.addstr(y-3, 1, "Notification:")
     for each in range(1, x-1):
          screen.addstr(y-4, each, "-")
     if page == "main_menu":
          screen.addstr(y-3, x-21, "(NC) = Not complete")
          screen.addstr(y-2, x-21, "(C)  = Complete")
     screen.addstr(y-2, 1, note)

     return y,x


##############################################################
#         Manage Model Screen
##############################################################

def load_model_screen(header):
     '''Generates screen to be able to load model file.
     Path to model file (netCDF) and variable name is required.

     :param header: Header of page
     :type header: string

     :returns: Notification
     :rtype: string
     '''

     ready_screen("load_model_screen")
     screen.addstr(1, 1, header + " > Load Model File ")
     screen.addstr(4, 2, "Enter model path: ")
     model_path = screen.getstr()
     try:
          netCDF_file = Dataset(model_path, 'r')
          all_netcdf_variables = [variable.encode() for variable in netCDF_file.variables.keys()]
          netCDF_file.close()
          try:
               screen.addstr(6, 2, "Enter model variable name {0}: ".format(all_netcdf_variables))
               variable_name = screen.getstr()
               model_dataset = load_file(model_path, variable_name)
               model_datasets.append(model_dataset)
               models_info.append({ 'directory': model_path,
                                 'variable_name': variable_name
                              })
               note = "Model file successfully added."
          except:
               note = "WARNING: Model file cannot be added. The variable [{0}] is not accepted. Please try again.".format(variable_name)
     except:
          note = "WARNING: Model file cannot be read. Please check the file directory or format. Only netCDF format is accepted."

     return note



def unload_model_screen(header):
     '''Generates screen to be able to unload model file.
     It lists all loaded model with index for each.
     Selection of model with index will remove model from list of models.

     :param header: Header of page
     :type header: string

     :returns: Notification
     :rtype: string
     '''

     ready_screen("unload_model_screen")
     screen.addstr(1, 1, header + " > Unload Model File")
     screen.addstr(6, 1, "List of Model:")
     for i, model in enumerate(models_info):
          screen.addstr(8 + i, 10,  "Model Number:[{0}] - Model path:[{1}] - Variables:[{2}]".format(str(i), model['directory'], model['variable_name']))
     screen.addstr(3, 2, "Select the model number to remove (press enter to go back): ")
     try:
          model_remove_index = screen.getstr()
          models_info.pop(int(model_remove_index))
          model_datasets.pop(int(model_remove_index))
          note = "Model file unloaded successfully"
     except:
          note = "WARNING: Model file was not unloaded successfully."

     return note


def list_model_screen(header):
     '''Generates screen to list all model files.

     :param header: Header of page
     :type header: string
     '''

     ready_screen("list_model_screen")
     screen.addstr(1, 1, header + " > List Model File ")
     screen.addstr(6, 6, "List of model(s): ")
     for i, model in enumerate(models_info):
          screen.addstr(8 + i, 10,  "Model Number:[{0}] - Model path:[{1}] - Variables:[{2}]".format(str(i), model['directory'], model['variable_name']))
     screen.addstr(4, 4, "Return to Manage Model (press Enter) :")
     screen.getstr()


def manage_model_screen(header, note = ""):
     '''Generates Manage Model screen.

     :param header: Header of page
     :type header: string
     :param note: Notification, defult to empty string.
     :type note: string
     '''

     option = ''
     while option != '0':
          ready_screen("manage_model_screen", note)
          screen.addstr(1, 1, header)
          screen.addstr(4, 4, "1 - Load Model File     [Number of loaded model: {0}]".format(len(model_datasets)))
          screen.addstr(6, 4, "2 - Unload Model File")
          screen.addstr(8, 4, "3 - List Model File")
          screen.addstr(10, 4, "0 - Return to Main Menu")
          screen.addstr(12, 2, "Select an option: ")
          screen.refresh()
          option = screen.getstr()

          if option == '1':
               note = load_model_screen(header)
          if option == '2':
               note = unload_model_screen(header)
          if option == '3':
               note = list_model_screen(header)
               note = " "


##############################################################
#     Manage Observation Screen
##############################################################

def select_obs_screen(header):   #TODO: if the observation is already selected, don't select again.
     '''Generates screen to select observation.
     It reterives list of observations from database and make a table from that.
     User has to select observation with dataset_id, parameter_id, start_date, end_date, minimum and maximum of lat and lon.
     If the size of terminal screen is small to show whole table, a notification with link to parameter table on website will show up instead.

     :param header: Header of page
     :type header: string

     :returns: Notification
     :rtype: string
     '''

     ready_screen("select_obs_screen")
     screen.addstr(1, 1, header + " > Select Observation ")
     screen.addstr(8, 1, "Observations Table: ")
     screen.addstr(9, 2, "|Dataset ID| - |Parameter ID| - |Time Step| - |Start Date| - | End Date | - | Min Lat | - | Max Lat | - | Min Lon | - | Max Lat | - |Database name")
     screen.addstr(10, 2, "|----------| - |------------| - |---------| - |----------| - |----------| - |---------| - |---------| - |---------| - |---------| - |-------------")
     all_obs_info = rcmed.get_parameters_metadata()
     try:
          for position, obs_info in enumerate(all_obs_info):
               dataset_id = obs_info['dataset_id']
               parameter_id = obs_info['parameter_id']
               timestep = obs_info ['timestep']
               start_date = obs_info ['start_date']
               end_date = obs_info ['end_date']
               min_lat = eval(obs_info['bounding_box'].encode())[2][0] if obs_info['bounding_box'] else None
               max_lat = eval(obs_info['bounding_box'].encode())[0][0] if obs_info['bounding_box'] else None
               min_lon = eval(obs_info['bounding_box'].encode())[2][1] if obs_info['bounding_box'] else None
               max_lon = eval(obs_info['bounding_box'].encode())[0][1] if obs_info['bounding_box'] else None
               database = obs_info ['database']
               line = "|{0:>10}| - |{1:>12}| - |{2:>9}| - |{3}| - |{4}| - |{5:>9}| - |{6:>9}| - |{7:>9}| - |{8:>9}| - |{9}".format(
                    dataset_id, parameter_id, timestep, start_date, end_date,
                    str(min_lat), str(max_lat), str(min_lon), str(max_lon), database)
               screen.addstr(11 + position, 2, line)
     except:
          ready_screen("select_obs_screen")
          screen.addstr(1, 1, header + " > Select Observation ")
          screen.addstr(10, 1, "Observation table cannot be shown due to small screen size. ")
          screen.addstr(11, 1, "Please enlarge your screen and try again or refer to 'http://rcmes.jpl.nasa.gov/rcmed/parameters'. ")
     try:
          screen.addstr(4, 2, "Enter Dataset ID: ")
          dataset_id = screen.getstr()
          screen.addstr(5, 2, "Enter Parameter ID: ")
          parameter_id = screen.getstr()

          for obs in all_obs_info:
               if obs['dataset_id'] == dataset_id and obs['parameter_id'] == parameter_id:
                    observations_info.append({
                                        'database':obs['database'],
                                        'dataset_id':dataset_id,
                                        'parameter_id':parameter_id,
                                        'start_date':obs['start_date'],
                                        'end_date':obs['end_date'],
                                        'bounding_box':obs['bounding_box'],
                                        'timestep':obs['timestep'],
                                        'min_lat':float(eval(obs['bounding_box'].encode())[2][0]) if obs['bounding_box'] else None,
                                        'max_lat':float(eval(obs['bounding_box'].encode())[0][0]) if obs['bounding_box'] else None,
                                        'min_lon':float(eval(obs['bounding_box'].encode())[2][1]) if obs['bounding_box'] else None,
                                        'max_lon':float(eval(obs['bounding_box'].encode())[0][1]) if obs['bounding_box'] else None,
                                        'timestep':obs['timestep'],
                                        'timestep':obs['timestep'],
                                        'timestep':obs['timestep'],
                                        'lat_res':float(obs['lat_res'].encode()),
                                        'lon_res':float(obs['lon_res'].encode())
                                        })
                    note = "Observation sucessfully selected."
                    break
               else:
                    note = "WARNING: Observation cannot be selected. There is no observation with given info."
     except:
          note = "WARNING: Observation cannot be selected, dataset or parameter id is wrong."

     return  note


def unselect_obs_screen(header):
     '''Generates screen to be able to unselect observations.
     Observations can be unselected by entering index allocated to them.

     :param header: Header of page
     :type header: string

     :returns: Notification
     :rtype: string
     '''

     ready_screen("unselect_obs_screen")
     screen.addstr(1, 1, header + " > Unselect Observation ")
     screen.addstr(6, 1, "List Observation(s):")
     for i, obs_info in enumerate(observations_info):
          screen.addstr(8 + i, 10, " [" + str(i) + "] : " + " Dataset ID: " + obs_info['dataset_id'] + " - Parameter ID: "+ obs_info['parameter_id'] + " - Database: "+ obs_info['database'])
     screen.addstr(3, 2, "Select the observation to remove (press enter to go back): ")
     try:
          obs_remove_index = screen.getstr()
          observations_info.pop(int(obs_remove_index))
          note = "Observation sucessfully unselected."
     except:
          note = "WARNING: Unselecting model was not successful."

     return note


def list_obs_screen(header):
     '''Generates screen to list observations.

     :param header: Header of page
     :type header: string
     '''

     ready_screen("list_obs_screen")
     screen.addstr(1, 1, header + " > List Observation ")
     screen.addstr(6, 6, "List of observation(s): ")
     for i, obs_info in enumerate(observations_info):
          screen.addstr(8 + i, 10, " [" + str(i) + "] : " + " Dataset ID: " + obs_info['dataset_id'] + " - Parameter ID: "+ obs_info['parameter_id'] + " - Database: "+ obs_info['database'])
     screen.addstr(4, 4, "Return to Manage Observation (press Enter) :")
     screen.getstr()


def manage_obs_screen(header, note = ""):
     '''Generates Manage Observation screen.

     :param header: Header of page
     :type header: string
     :param note: Notification, defult to empty string.
     :type note: string
     '''

     option = ''
     while option != '0':
          ready_screen("manage_obs_screen", note)
          screen.addstr(1, 1, header)
          screen.addstr(4, 4, "1 - Select Observation     [Number of selected observation: {0}]".format(len(observations_info)))
          screen.addstr(6, 4, "2 - Unselect Observation")
          screen.addstr(8, 4, "3 - List Observation")
          screen.addstr(10, 4, "0 - Return to Main Menu")
          screen.addstr(12, 2, "Select an option: ")
          screen.refresh()

          option = screen.getstr()
          if option == '1':
               note = select_obs_screen(header)
          if option == '2':
               note = unselect_obs_screen(header)
          if option == '3':
               list_obs_screen(header)
               note = " "


##############################################################
#     Run Evaluation Screen
##############################################################

def run_screen(model_datasets, models_info, observations_info,
               overlap_start_time, overlap_end_time, overlap_min_lat,
               overlap_max_lat, overlap_min_lon, overlap_max_lon,
               temp_grid_setting, spatial_grid_setting, working_directory, plot_title):
     '''Generates screen to show running evaluation process.

     :param model_datasets: list of model dataset objects
     :type model_datasets: list
     :param models_info: list of dictionaries that contain information for each model
     :type models_info: list
     :param observations_info: list of dictionaries that contain information for each observation
     :type observations_info: list
     :param overlap_start_time: overlap start time between model and obs start time
     :type overlap_start_time: datetime
     :param overlap_end_time: overlap end time between model and obs end time
     :type overlap_end_time: float
     :param overlap_min_lat: overlap minimum lat between model and obs minimum lat
     :type overlap_min_lat: float
     :param overlap_max_lat: overlap maximum lat between model and obs maximum lat
     :type overlap_max_lat: float
     :param overlap_min_lon: overlap minimum lon between model and obs minimum lon
     :type overlap_min_lon: float
     :param overlap_max_lon: overlap maximum lon between model and obs maximum lon
     :type overlap_max_lon: float
     :param temp_grid_setting: temporal grid option such as hourly, daily, monthly and annually
     :type temp_grid_setting: string
     :param spatial_grid_setting:
     :type spatial_grid_setting: string
     :param working_directory: path to a directory for storring outputs
     :type working_directory: string
     :param plot_title: Title for plot
     :type plot_title: string
     '''

     option = None
     if option != "0":
          ready_screen("manage_obs_screen")
          y = screen.getmaxyx()[0]
          screen.addstr(2, 2, "Evaluation started....")
          screen.refresh()

          OUTPUT_PLOT = "plot"

          dataset_id = int(observations_info[0]['dataset_id'])       #just accepts one dataset at this time
          parameter_id =  int(observations_info[0]['parameter_id'])  #just accepts one dataset at this time

          new_bounds = Bounds(overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon, overlap_start_time, overlap_end_time)
          model_dataset = dsp.subset(new_bounds, model_datasets[0])   #just accepts one model at this time

          #Getting bound info of subseted model file to retrive obs data with same bound as subseted model
          new_model_spatial_bounds = model_dataset.spatial_boundaries()
          new_model_temp_bounds = model_dataset.time_range()
          new_min_lat = new_model_spatial_bounds[0]
          new_max_lat = new_model_spatial_bounds[1]
          new_min_lon = new_model_spatial_bounds[2]
          new_max_lon = new_model_spatial_bounds[3]
          new_start_time = new_model_temp_bounds[0]
          new_end_time = new_model_temp_bounds[1]

          screen.addstr(4, 4, "Retrieving data...")
          screen.refresh()

          #Retrieve obs data
          obs_dataset = rcmed.parameter_dataset(
                                        dataset_id,
                                        parameter_id,
                                        new_min_lat,
                                        new_max_lat,
                                        new_min_lon,
                                        new_max_lon,
                                        new_start_time,
                                        new_end_time)
          screen.addstr(4, 4, "--> Data retrieved.")
          screen.refresh()

          screen.addstr(5, 4, "Temporally regridding...")
          screen.refresh()
          if temp_grid_setting.lower() == 'hourly':
               days = 0.5
          elif temp_grid_setting.lower() == 'daily':
               days = 1
          elif temp_grid_setting.lower() == 'monthly':
               days = 31
          else:
               days = 365
          model_dataset = dsp.temporal_rebin(model_dataset, timedelta(days))
          obs_dataset = dsp.temporal_rebin(obs_dataset, timedelta(days))
          screen.addstr(5, 4, "--> Temporally regridded.")
          screen.refresh()

          new_lats = np.arange(new_min_lat, new_max_lat, spatial_grid_setting)
          new_lons = np.arange(new_min_lon, new_max_lon, spatial_grid_setting)

          screen.addstr(6, 4, "Spatially regridding...")
          screen.refresh()
          spatial_gridded_model = dsp.spatial_regrid(model_dataset, new_lats, new_lons)
          spatial_gridded_obs = dsp.spatial_regrid(obs_dataset, new_lats, new_lons)
          screen.addstr(6, 4, "--> Spatially regridded.")
          screen.refresh()

          screen.addstr(7, 4, "Setting up metrics...")
          screen.refresh()
          bias = metrics.Bias()
          bias_evaluation = evaluation.Evaluation(spatial_gridded_model, [spatial_gridded_obs], [bias])
          screen.addstr(7, 4, "--> Metrics setting done.")
          screen.refresh()

          screen.addstr(8, 4, "Running evaluation.....")
          screen.refresh()
          bias_evaluation.run()
          results = bias_evaluation.results[0][0]
          screen.addstr(8, 4, "--> Evaluation Finished.")
          screen.refresh()

          screen.addstr(9, 4, "Generating plots....")
          screen.refresh()
          lats = new_lats
          lons = new_lons

          gridshape = (1, 1)
          sub_titles = [""]   #No subtitle set for now

          if not os.path.exists(working_directory):
               os.makedirs(working_directory)

          for i in range(len(results)):
               fname = working_directory + OUTPUT_PLOT + str(i)
               plotter.draw_contour_map(results[i], lats, lons, fname,
                               gridshape=gridshape, ptitle=plot_title,
                               subtitles=sub_titles)
          screen.addstr(9, 4, "--> Plots generated.")
          screen.refresh()
          screen.addstr(y-2, 1, "Press 'enter' to Exit: ")
          option = screen.getstr()


##############################################################
#     Settings Screen
##############################################################

def get_model_temp_bound():
     '''Get model temporal bound.

     :returns: model start and end time
     :rtypes: (datatime, datetime)
     '''

     model_start_time = model_datasets[0].time_range()[0]    #just accepts one model at this time
     model_end_time = model_datasets[0].time_range()[1]      #just accepts one model at this time

     return model_start_time, model_end_time


def get_obs_temp_bound():
     '''Get observation temporal bound.

     :returns: observation start and end time
     :rtype: (datetime, datetime)
     '''

     obs_start_time = observations_info[0]['start_date']    #just accepts one obs at this time
     obs_end_time = observations_info[0]['end_date']        #just accepts one obs at this time
     obs_start_time = datetime.strptime(obs_start_time, "%Y-%m-%d")
     obs_end_time = datetime.strptime(obs_end_time, "%Y-%m-%d")

     return obs_start_time, obs_end_time


def get_temp_overlap(model_start_time, model_end_time, obs_start_time, obs_end_time):
     '''Calculate temporal overlap between given datasets.

     :param model_start_time: model start time
     :type model_start_time: datetime
     :param model_end_time: model end time
     :type model_end_time: datetime
     :param obs_start_time: obs start time
     :type obs_start_time: datetime
     :param obs_end_time: obs end time
     :type obs_end_time: datetime

     :returns: overlap start and end time between model and observation
     :rtype: (datetime, datetime)
     '''

     overlap_start_time = max(model_start_time, obs_start_time)
     overlap_end_time = min(model_end_time, obs_end_time)

     return overlap_start_time, overlap_end_time


def get_model_spatial_bound():               #TODO: convert longitudes to -180, 180 to match with observation data
     '''Get model spatial bound.

     :returns: model spatial boundaries
     :rtype: (float, float, float, float)
     '''

     model_bound = model_datasets[0].spatial_boundaries()    #just accepts one model at this time
     model_min_lat = model_bound[0]
     model_max_lat = model_bound[1]
     model_min_lon = model_bound[2]
     model_max_lon = model_bound[3]

     return model_min_lat, model_max_lat, model_min_lon, model_max_lon


def get_obs_spatial_bound():
     '''Get observation spatial bound.

     :returns: observation spatial boundaries
     :rtype: (float, float, float, float)
     '''

     obs_min_lat = observations_info[0]['min_lat']     #just accepts one obs at this time
     obs_max_lat = observations_info[0]['max_lat']     #just accepts one obs at this time
     obs_min_lon = observations_info[0]['min_lon']     #just accepts one obs at this time
     obs_max_lon = observations_info[0]['max_lon']     #just accepts one obs at this time

     return obs_min_lat, obs_max_lat, obs_min_lon, obs_max_lon


def get_spatial_overlap(model_min_lat, model_max_lat, model_min_lon, model_max_lon, obs_min_lat, obs_max_lat, obs_min_lon, obs_max_lon):
     '''Calculate spatial overlap between given datasets.

     :param model_min_lat: model minumum latitude
     :type model_min_lat: float
     :param model_max_lat: model maximum latitude
     :type model_max_lat: float
     :param model_min_lon: model minimum longitude
     :type model_min_lon: float
     :param model_max_lon: model maximum longitude
     :type model_max_lon: float
     :param obs_min_lat: observation minimum latitude
     :type obs_min_lat: float
     :param obs_max_lat: observation maximum latitude
     :type obs_max_lat: float
     :param obs_min_lon: observation minimum longitude
     :type obs_min_lon: float
     :param obs_max_lon: observation maximum longitude
     :type obs_max_lon: float

     :returns: spatial boundaries overlap between model and observation
     :rtype: (float, float, float, float)
     '''

     overlap_min_lat = max(model_min_lat, obs_min_lat)
     overlap_max_lat = min(model_max_lat, obs_max_lat)
     overlap_min_lon = max(model_min_lon, obs_min_lon)
     overlap_max_lon = min(model_max_lon, obs_max_lon)

     return overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon


def settings_screen(header):
     '''Generates screen for settings before running evaluation.

     :param header: Header of page
     :type header: string
     '''

     note = ""
     model_start_time, model_end_time = get_model_temp_bound()
     obs_start_time, obs_end_time = get_obs_temp_bound()
     overlap_start_time, overlap_end_time = get_temp_overlap(model_start_time, model_end_time, obs_start_time, obs_end_time)
     model_min_lat, model_max_lat, model_min_lon, model_max_lon = get_model_spatial_bound()
     obs_min_lat, obs_max_lat, obs_min_lon, obs_max_lon = get_obs_spatial_bound()
     overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon = get_spatial_overlap(model_min_lat, model_max_lat, model_min_lon, model_max_lon, obs_min_lat, obs_max_lat, obs_min_lon, obs_max_lon)
     model_temp_res = model_datasets[0].temporal_resolution()       #just accepts one model at this time
     obs_temp_res = observations_info[0]['timestep']        #just accepts one obs at this time
     model_lat_res = model_datasets[0].spatial_resolution()[0] #just accepts one model at this time
     model_lon_res = model_datasets[0].spatial_resolution()[1]  #just accepts one model at this time
     obs_lat_res = observations_info[0].observations_info['lat_res']     #just accepts one obs at this time
     obs_lon_res = observations_info[0].observations_info['lon_res']    #just accepts one obs at this time

     temp_grid_option = "Observation"
     temp_grid_setting = obs_temp_res
     spatial_grid_option = "Observation"
     spatial_grid_setting = obs_lat_res
     subregion_path = None
     metrics = 'BIAS'
     working_directory = os.getcwd() + "/plots/"  #Default value of working directory set to "plots" folder in current directory
     plot_title = '' #TODO: ask user about plot title or figure out automatically

     fix_min_time = overlap_start_time
     fix_max_time = overlap_end_time
     fix_min_lat = overlap_min_lat
     fix_max_lat = overlap_max_lat
     fix_min_lon = overlap_min_lon
     fix_max_lon = overlap_max_lon

     option = ''
     while option != '0':
          ready_screen("settings_screen", note)
          screen.addstr(1, 1, header)
          screen.addstr(4, 4, "Number of model file:   {0}".format(str(len(model_datasets))))
          screen.addstr(5, 4, "Number of observation:  {0}".format(str(len(observations_info))))
          screen.addstr(6, 4, "Temporal Boundaries:    [start time = {0} - end time = {1}]".format(overlap_start_time, overlap_end_time))
          screen.addstr(7, 4, "Spatial Boundaries:     [min-lat={0}  max-lat={1} min-lon={2} max-lon={3}]".format(overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon))
          screen.addstr(8, 4, "Temporal Resolution:    [Model={0} - Observation={1}]".format(model_temp_res, obs_temp_res))
          screen.addstr(9, 4, "Spatial Resolution:     [Model: lat={0} lon={1} - Observation: lat={2} lon={3}]".format(model_lat_res, model_lon_res, obs_lat_res, obs_lon_res))
          screen.addstr(10, 4, "Temporal Grid Option:   [{0}]".format(temp_grid_option))
          screen.addstr(11, 4, "Spatial Grid Option:    [{0}]".format(spatial_grid_option))
          screen.addstr(12, 4, "Working Directory:      {0}".format(working_directory))
          screen.addstr(13, 4, "Metrics:                {0}".format(metrics))

          screen.addstr(15, 5, "1 - Change Temporal Boundaries")
          screen.addstr(16, 5, "2 - Change Spatial Boundaries")
          screen.addstr(17, 5, "3 - Change Temporal Gridding")
          screen.addstr(18, 5, "4 - Change Spatial Gridding")
          screen.addstr(19, 5, "5 - Add Subregion file (txt file) [Coming Soon....]")
          screen.addstr(20, 5, "6 - Modify Metric (add/remove) [Coming Soon....]")
          screen.addstr(21, 5, "7 - Change Working Directory")
          screen.addstr(22, 5, "8 - Change Plot Title [Coming Soon....]")
          screen.addstr(23, 5, "0 - Return to Main Menu")
          screen.addstr(26, 5, "r - Run Evaluation")
          screen.addstr(28, 2, "Select an option: ")

          screen.refresh()
          option = screen.getstr()
          ### TODO: It breaks when you want to pick start time after end time and same issue with lat, lon.

          if option == '1':
               screen.addstr(33, 4, "Enter Start Time [min time: {0}] (Format YYYY-MM-DD):".format(fix_min_time))
               new_start_time = screen.getstr()
               try:
                    new_start_time = datetime.strptime(new_start_time, '%Y-%m-%d')
                    if new_start_time < fix_min_time or new_start_time > fix_max_time or new_start_time > overlap_end_time:
                         note = "Start time has not changed."
                    else:
                         overlap_start_time = new_start_time
                         note = "Start time has changed successfully."
               except:
                    note = "Start time has not changed."
               screen.addstr(34, 4, "Enter End Time [max time:{0}] (Format YYYY-MM-DD):".format(fix_max_time))
               new_max_time = screen.getstr()
               try:
                    new_max_time = datetime.strptime(new_max_time, '%Y-%m-%d')
                    if new_max_time > fix_max_time or new_max_time < fix_min_time or new_max_time < overlap_start_time:
                         note = note + " End time has not changed."
                    else:
                         overlap_end_time = new_max_time
                         note = note + "End time has changed successfully."
               except:
                    note = note + " End time has not changed."

          if option == '2':
               screen.addstr(33, 4, "Enter Minimum Latitude [{0}]:".format(fix_min_lat))
               new_min_lat = screen.getstr()
               try:
                    new_min_lat = float(new_min_lat)
                    if new_min_lat < fix_min_lat or new_min_lat > fix_max_lat or new_min_lat > overlap_max_lat:
                         note = "Minimum latitude has not changed."
                    else:
                         overlap_min_lat = new_min_lat
                         note = "Minimum latitude has changed successfully."
               except:
                    note = "Minimum latitude has not changed."
               screen.addstr(34, 4, "Enter Maximum Latitude [{0}]:".format(fix_max_lat))
               new_max_lat = screen.getstr()
               try:
                    new_max_lat = float(new_max_lat)
                    if new_max_lat > fix_max_lat or new_max_lat < fix_min_lat or new_max_lat < overlap_min_lat:
                         note = note + " Maximum latitude has not changed."
                    else:
                         overlap_max_lat = new_max_lat
                         note = note + "Maximum latitude has changed successfully."
               except:
                    note = note + " Maximum latitude has not changed."
               screen.addstr(35, 4, "Enter Minimum Longitude [{0}]:".format(fix_min_lon))
               new_min_lon = screen.getstr()
               try:
                    new_min_lon = float(new_min_lon)
                    if new_min_lon < fix_min_lon or new_min_lon > fix_max_lon or new_min_lon > overlap_max_lon:
                         note = note + " Minimum longitude has not changed."
                    else:
                         overlap_min_lon = new_min_lon
                         note = note + "Minimum longitude has changed successfully."
               except:
                    note = note + " Minimum longitude has not changed."
               screen.addstr(36, 4, "Enter Maximum Longitude [{0}]:".format(fix_max_lon))
               new_max_lon = screen.getstr()
               try:
                    new_max_lon = float(new_max_lon)
                    if new_max_lon > fix_max_lon or new_max_lon < fix_min_lon or new_max_lon < overlap_min_lon:
                         note = note + " Maximum longitude has not changed."
                    else:
                         overlap_max_lon = new_max_lon
                         note = note + "Maximum longitude has changed successfully."
               except:
                    note = note + " Maximum longitude has not changed."

          if option == '3':
               screen.addstr(33, 4, "Enter Temporal Gridding Option [Model or Observation]:")
               new_temp_grid_option = screen.getstr()
               if new_temp_grid_option.lower() == 'model':
                    temp_grid_option = 'Model'
                    temp_grid_setting = model_temp_res
                    note = "Temporal gridding option has changed successfully to {0}".format(temp_grid_option)
               elif new_temp_grid_option.lower() == 'observation':
                    temp_grid_option = 'Observation'
                    temp_grid_setting = obs_temp_res
                    note = "Temporal gridding option has changed successfully to {0}".format(temp_grid_option)
               else:
                    note = "Temporal gridding option has not be changed."

          if option == '4':
               screen.addstr(33, 4, "Enter Spatial Gridding Option [Model, Observation or User]:")
               new_spatial_grid_option = screen.getstr()
               if new_spatial_grid_option.lower() == 'model':
                    spatial_grid_option = 'Model'
                    spatial_grid_setting = model_lat_res
                    note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
               elif new_spatial_grid_option.lower() == 'observation':
                    spatial_grid_option = 'Observation'
                    spatial_grid_setting = obs_lat_res
                    note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
               elif new_spatial_grid_option.lower() == 'user':
                    screen.addstr(34, 4, "Please enter spatial resolution: ")
                    user_res = screen.getstr()
                    try:
                         user_res = float(user_res)
                         spatial_grid_option = 'User: resolution {0}'.format(str(user_res))
                         spatial_grid_setting = user_res
                         note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
                    except:
                         note = "Spatial gridding option has not be changed."
               else:
                    note = "Spatial gridding option has not be changed."

          '''
          if option == '5':
               screen.addstr(33, 4, "Please enter one Subregion path:")
               subregion_path = screen.getstr()
          '''
          if option == '7':
               screen.addstr(33, 4, "Please enter working directory path:")
               working_directory = screen.getstr()
               if working_directory[-1] != '/':
                    working_directory = working_directory + "/"

          if option == '8':
               screen.addstr(33, 4, "Please enter plot title:")
               plot_title = screen.getstr()

          if option.lower() == 'r':
               run_screen(model_datasets, models_info, observations_info, overlap_start_time, overlap_end_time, \
                          overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon, \
                          temp_grid_setting, spatial_grid_setting, working_directory, plot_title)


##############################################################
#     Main Menu Screen
##############################################################

def main_menu(model_datasets, models_info, observation_datasets, observations_info, note = ""):
     '''This function Generates main menu page.

     :param model_datasets: list of model dataset objects
     :type model_datasets: list
     :param models_info: list of dictionaries that contain information for each model
     :type models_info: list
     :param observation_datasets: list of observation dataset objects
     :type observation_datasets: list
     :param observations_info: list of dictionaries that contain information for each observation
     :type observations_info: list
     '''

     option = ''
     while option != '0':
          ready_screen("main_menu", note='')
          model_status = "NC" if len(model_datasets) == 0 else "C"     #NC (Not Complete), if there is no model added, C (Complete) if model is added
          obs_status = "NC" if len(observations_info) == 0 else "C"    #NC (Not Complete), if there is no observation added, C (Complete) if observation is added
          screen.addstr(1, 1, "Main Menu:")
          screen.addstr(4, 4, "1 - Manage Model ({0})".format(model_status))
          screen.addstr(6, 4, "2 - Manage Observation ({0})".format(obs_status))
          screen.addstr(8, 4, "3 - Run(Config File) [coming soon....]")
          screen.addstr(10, 4, "4 - Run(Settings)")
          screen.addstr(12, 4, "0 - EXIT")
          screen.addstr(18, 2, "Select an option: ")
          screen.refresh()
          option = screen.getstr()

          if option == '1':
               header = "Main Menu > Manage Model"
               manage_model_screen(header)
          if option == '2':
               header = "Main Menu > Manage Observation"
               manage_obs_screen(header)
          if option == '3':
               header = "Main Menu > Run(Config File)"
               #TODO: function to read config file and run evaluation
          if option == '4':
               if model_status =='NC' or obs_status == 'NC':
                    main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: Please complete step 1 and 2 before 4.")
               else:
                    header = "Main Menu > Run(Settings)"
                    settings_screen(header)
     curses.endwin()
     sys.exit()


if __name__ == '__main__':
     TITLE = "Open Climate Workbench Evaluation System"
     ORGANIZATION = "Apache Software Foundation"
     screen = curses.initscr()
     model_datasets = []           #list of model dataset objects
     models_info = []              #list of dictionaries that contain information for each model
     observation_datasets = []     #list of observation dataset objects
     observations_info = []        #list of dictionaries that contain information for each observation
     main_menu(model_datasets, models_info, observation_datasets, observations_info)
