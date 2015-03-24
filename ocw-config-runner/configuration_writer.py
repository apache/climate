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

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

def generate_dataset_information(dataset):
    ''' Generates a dict of dataset information for export.

    :param dataset: The dataset from which to extract configuration
        information.
    :type dataset: :class:`dataset.Dataset`

    :returns: :func:`dict` containing necessary information for
        dataset to be saved into a configuration object.

    :raises AttributeError: If dataset does not contain expected source data.
    '''
    dataset_source = dataset.origin['source']

    if dataset_source == 'local':
        info = _extract_local_dataset_info(dataset)
    elif dataset_source == 'rcmed':
        info = _extract_rcmed_dataset_info(dataset)
    elif dataset_source == 'esgf':
        info = _extract_esgf_dataset_info(dataset)
    elif dataset_source == 'dap':
        info = _extract_dap_dataset_info(dataset)
    else:
        err = (
            "Unexpected source in dataset origin information."
            "Found {}."
        ).format(dataset_source)
        logger.error(err)
        raise AttributeError(err)

    info['optional_args']['name'] = dataset.name
    info['optional_args']['units'] = dataset.units

    return info

def generate_metric_information(evaluation):
    ''' Generate metric config file output from a given Evaluation object.

    :param evaluation: The evaluation object from which to extract metrics.
    :type evaluation: :class:`evaluation.Evaluation`

    :returns: A :func:`list` of :mod:`metrics` object names for output into
        a configuration file.
    :rtype: :func:`list` of :mod:`metrics`
    '''
    unary_metrics = [x.__class__.__name__ for x in evaluation.unary_metrics]
    binary_metrics = [x.__class__.__name__ for x in evaluation.metrics]

    return unary_metrics + binary_metrics

def _extract_local_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'local'
    dataset_info['file_count'] = 1
    dataset_info['path'] = dataset.origin['path']
    dataset_info['variable'] = dataset.variable

    dataset_info['optional_args']['lat_name'] = dataset.origin['lat_name']
    dataset_info['optional_args']['lon_name'] = dataset.origin['lon_name']
    dataset_info['optional_args']['time_name'] = dataset.origin['time_name']

    if 'elevation_index' in dataset.origin:
        elev = dataset.origin['elevation_index']
        dataset_info['optional_args']['elevation_index'] = elev

    return dataset_info

def _extract_rcmed_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    min_lat, max_lat, min_lon, max_lon = dataset.spatial_boundaries()
    start_time, end_time = dataset.time_range()

    dataset_info['data_source'] = 'rcmed'
    dataset_info['dataset_id'] = dataset.origin['dataset_id']
    dataset_info['parameter_id'] = dataset.origin['parameter_id']
    dataset_info['min_lat'] = min_lat
    dataset_info['max_lat'] = max_lat
    dataset_info['min_lon'] = min_lon
    dataset_info['max_lon'] = max_lon
    dataset_info['start_time'] = str(start_time)
    dataset_info['end_time'] = str(end_time)

    return dataset_info

def _extract_esgf_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'esgf'
    dataset_info['dataset_id'] = dataset.origin['dataset_id']
    dataset_info['variable'] = dataset.origin['variable']
    dataset_info['esgf_username'] = 'Put your ESGF Username here'
    dataset_info['esgf_password'] = 'Put your ESGF Password here'

    return dataset_info

def _extract_dap_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'dap'
    dataset_info['url'] = dataset.origin['url']
    dataset_info['variable'] = dataset.variable

    return dataset_info
