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

'''
Classes:
    Dataset - Container for a dataset's attributes and data.
'''

import numpy
import logging

class Dataset:
    '''Container for a dataset's attributes and data.'''

    def __init__(self, lats, lons, times, values, variable=None):
        '''Default Dataset constructor

        :param lats: One dimensional numpy array of unique latitude values.
        :type lats: numpy array
        :param lons: One dimensional numpy array of unique longitude values.
        :type lons: numpy array
        :param times: One dimensional numpy array of unique python datetime 
            objects.
        :type times: numpy array
        :param values: Three dimensional numpy array of parameter values with 
            shape [timesLength, latsLength, lonsLength]. 
        :type values: numpy array
        :param variable: Name of the value variable.
        :type variable: string
        '''
        self.lats = lats
        self.lons = lons
        self.times = times
        self.values = values
        self.variable = variable

    def spatial_boundaries(self):
        '''Calculate the spatial boundaries.

        :returns: The Dataset's bounding latitude and longitude values as a
            tuple in the form (min_lat, max_lat, min_lon, max_lon)
        :rtype: (float, float, float, float)

        '''
        return (min(self.lats), max(self.lats),
                min(self.lons), max(self.lons))


    def time_range(self):
        '''Calculate the temporal range

        :returns: The start and end date of the Dataset's temporal range as 
            a tuple in the form (start_time, end_time).
        :rtype: (datetime, datetime)
        '''
        sorted_time = numpy.sort(self.times)
        start_time = sorted_time[0]
        end_time = sorted_time[-1]

        return (start_time, end_time)


    def spatial_resolution(self):
        '''Calculate the latitudinal and longitudinal spatial resolution.

        .. warning:: This only works with properly gridded data.

        :returns: The Dataset's latitudinal and longitudinal spatial resolution
            as a tuple of the form (lat_resolution, lon_resolution).
        :rtype: (float, float)
        '''
        sorted_lats = numpy.sort(list(set(self.lats)))
        sorted_lons = numpy.sort(list(set(self.lons)))
        lat_resolution = sorted_lats[1] - sorted_lats[0]
        lon_resolution = sorted_lons[1] - sorted_lons[0]

        return (lat_resolution, lon_resolution)


    def temporal_resolution(self):
        '''Calculate the temporal resolution.

        :raises ValueError: If timedelta.days as calculated from the sorted \
            list of times is an unrecognized value a ValueError is raised.

        :returns: The temporal resolution.
        :rtype: string
        '''
        sorted_times = numpy.sort(self.times)
        time_resolution = sorted_times[1] - sorted_times[0]
        num_days = time_resolution.days

        if num_days == 0:
            num_hours = time_resolution.seconds / 3600
            time_resolution = 'hourly' if num_hours >= 1 else 'minutely'
        elif num_days == 1:
            time_resolution = 'daily'
        elif num_days <= 31:
            time_resolution = 'monthly'
        elif num_days > 31:
            time_resolution = 'yearly'
        else:
            error = (
                "Unable to calculate the temporal resolution for the "
                "dataset. The number of days between two time values is "
                "an unexpected value: " + str(num_days)
            )

            logging.error(error)
            raise ValueError(error)

        return time_resolution
