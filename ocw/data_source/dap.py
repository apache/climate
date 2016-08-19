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

from pydap.client import open_url
from netcdftime import utime
import numpy as np
from ocw.dataset import Dataset


def load(url, variable, name=''):
    '''Load a Dataset from an OpenDAP URL

    :param url: The OpenDAP URL for the dataset of interest.
    :type url: :mod:`string`

    :param variable: The name of the variable to read from the dataset.
    :type variable: :mod:`string`

    :param name: (Optional) A name for the loaded dataset.
    :type name: :mod:`string`

    :returns: A :class:`dataset.Dataset` containing the dataset pointed to by
        the OpenDAP URL.

    :raises: ServerError
    '''
    # Grab the dataset information and pull the appropriate variable
    d = open_url(url)
    dataset = d[variable]

    # By convention, but not by standard, if the dimensions exist, they will be in the order:
    # time (t), altitude (z), latitude (y), longitude (x)
    # but conventions aren't always followed and all dimensions aren't always present so
    # see if we can make some educated deductions before defaulting to just pulling the first three
    # columns.
    temp_dimensions = map(lambda x: x.lower(), dataset.dimensions)

    dataset_dimensions = dataset.dimensions
    time = dataset_dimensions[temp_dimensions.index(
        'time') if 'time' in temp_dimensions else 0]
    lat = dataset_dimensions[temp_dimensions.index(
        'lat') if 'lat' in temp_dimensions else 1]
    lon = dataset_dimensions[temp_dimensions.index(
        'lon') if 'lon' in temp_dimensions else 2]

    # Time is given to us in some units since an epoch. We need to convert
    # these values to datetime objects. Note that we use the main object's
    # time object and not the dataset specific reference to it. We need to
    # grab the 'units' from it and it fails on the dataset specific object.
    times = np.array(convert_times_to_datetime(d[time]))

    lats = np.array(dataset[lat][:])
    lons = np.array(dataset[lon][:])
    values = np.array(dataset[:])

    origin = {
        'source': 'dap',
        'url': url
    }

    return Dataset(lats, lons, times, values, variable,
                   name=name, origin=origin)


def convert_times_to_datetime(time):
    '''Convert the OpenDAP time object's values to datetime objects

    The time values are stored as some unit since an epoch. These need to be
    converted into datetime objects for the OCW Dataset object.

    :param time: The time object's values to convert
    :type time: pydap.model.BaseType

    :returns: list of converted time values as datetime objects
    '''
    units = time.units
    # parse the time units string into a useful object.
    # NOTE: This assumes a 'standard' calendar. It's possible (likely?) that
    #   users will want to customize this in the future.
    parsed_time = utime(units)
    return [parsed_time.num2date(x) for x in time[:]]
