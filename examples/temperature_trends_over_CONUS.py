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

import numpy as np
import datetime

# import Apache OCW dependences
import ocw.data_source.local as local
from ocw.dataset import Bounds as Bounds
import ocw.dataset_processor as dsp
import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.utils as utils
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# nClimDiv observation file
file_obs = 'nClimDiv/nClimDiv_tave_1895-2005.nc'

# temporal boundary
start_date = datetime.datetime(1979, 12, 1)
end_date = datetime.datetime(2005, 8, 31)

month_start = 6 # June
month_end = 8   # August

regions = []
regions.append(['WA', 'OR', 'ID'])
regions.append(['CA', 'NV', 'AZ', 'NM', 'UT','CO'])
regions.append(['MT', 'WY', 'ND', 'SD', 'NE'])
regions.append(['KS', 'TX', 'OK'])
regions.append(['MN', 'IA', 'MO', 'WI', 'IL', 'IN', 'MI','OH'])
regions.append(['ME', 'VT', 'NH', 'MA', 'NY', 'CT', 'RI','NJ','PA','WV','DE', 'MD'])
regions.append(['KY', 'VA', 'AR','AL', 'LA','MS', 'FL', 'GA','NC','SC', 'DC','TN'])

plotter.fill_US_states_with_color(regions, 'NCA_seven_regions', colors=True,
                                region_names=['NW','SW','NGP','SGP','MW','NE','SE'])

# CONUS regional boundaries
NW_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[0])
SW_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[1])
NGP_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[2])
SGP_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[3])
MW_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[4])
NE_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[5])
SE_bounds = Bounds(boundary_type='us_states', 
                   us_states=regions[6])


""" Load nClimDiv file into OCW Dataset """
obs_dataset = local.load_file(file_obs, variable_name='tave') 

""" Temporal subset of obs_dataset """
obs_dataset_subset = dsp.temporal_slice(obs_dataset, 
                  start_time=start_date, end_time=end_date)
obs_dataset_season = dsp.temporal_subset(obs_dataset_subset, month_start, month_end,
                      average_each_year=True)
""" Spatial subset of obs_dataset and generate time series """
NW_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, NW_bounds)) 
SW_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, SW_bounds)) 
NGP_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, NGP_bounds)) 
SGP_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, SGP_bounds)) 
MW_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, MW_bounds)) 
NE_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, NE_bounds)) 
SE_timeseries = utils.calc_time_series(dsp.subset(obs_dataset_season, SE_bounds)) 

year = np.arange(len(NW_timeseries))

regional_trends=[]
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, NW_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, SW_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, NGP_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, SGP_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, MW_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, NE_timeseries)[0])
regional_trends.append(utils.calculate_temporal_trend_of_time_series(year, SE_timeseries)[0])

plotter.fill_US_states_with_color(regions, 'NCA_tave_trends_JJA_1980-2005', 
                                  values=regional_trends,
                                  region_names=['%.3f' %(10*i) for i in regional_trends])

