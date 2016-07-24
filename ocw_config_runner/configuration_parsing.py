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
import re
import sys

import ocw.metrics as metrics

import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)

def is_config_valid(config_data):
    """ Validate supplied evaluation configuration data.

    :param config_data: Dictionary of the data parsed from the supplied YAML
        configuration file.
    :type config_data: :func:`dict`

    :returns: True if the configuration data is sufficient for an evaluation and
        seems to be well formed, False otherwise.
    """
    if not _valid_minimal_config(config_data):
        logger.error('Insufficient configuration file data for an evaluation')
        return False

    if not _config_is_well_formed(config_data):
        logger.error('Configuration data is not well formed')
        return False

    return True

def _valid_minimal_config(config_data):
    """"""
    if not 'datasets' in config_data.keys():
        logger.error('No datasets specified in configuration data.')
        return False

    if not 'metrics' in config_data.keys():
        logger.error('No metrics specified in configuration data.')
        return False

    if _contains_unary_metrics(config_data['metrics']):
        if (not 'reference' in config_data['datasets'].keys() and 
            not 'targets' in config_data['datasets'].keys()):
            err = (
                'Unary metric in configuration data requires either a reference '
                'or target dataset to be present for evaluation. Please ensure '
                'that your config is well formed.'
            )
            logger.error(err)
            return False

    if _contains_binary_metrics(config_data['metrics']):
        if (not 'reference' in config_data['datasets'].keys() or 
            not 'targets' in config_data['datasets'].keys()):
            logger.error(
                'Binary metric in configuration requires both a reference '
                'and target dataset to be present for evaluation. Please ensure '
                'that your config is well formed.'
            )
            return False

    return True

def _config_is_well_formed(config_data):
    """"""
    is_well_formed = True

    if 'reference' in config_data['datasets']:
        if not _valid_dataset_config_data(config_data['datasets']['reference']):
            is_well_formed = False

    if 'targets' in config_data['datasets']:
        targets = config_data['datasets']['targets']
        if type(targets) != type(list()):
            err = (
                'Expected to find list of target datasets but instead found '
                'object of type {}'
            ).format(type(targets))
            logger.error(err)
            is_well_formed = False
        else:
            for t in targets:
                if not _valid_dataset_config_data(t):
                    is_well_formed = False

    available_metrics = _fetch_built_in_metrics()
    for metric in config_data['metrics']:
        if metric not in available_metrics:
            warning = (
                'Unable to locate metric name {} in built-in metrics. If this '
                'is not a user defined metric then please check for potential '
                'misspellings.'
            ).format(metric)
            logger.warn(warning)
            is_well_formed = False

    if 'subregions' in config_data:
        for subregion in config_data['subregions']:
            if not _valid_subregion_config_data(subregion):
                is_well_formed = False

    if 'plots' in config_data:
        for plot in config_data['plots']:
            if not _valid_plot_config_data(plot):
                is_well_formed = False
            # Ensure that if we're trying to make a plot that require
            # subregion info that the config has this present.
            elif plot['type'] in ['subregion', 'portrait']:
                if ('subregions' not in config_data or
                    len(config_data['subregions']) < 1):
                    logger.error(
                        'Plot config that requires subregion information is present '
                        'in a config file without adequate subregion information '
                        'provided. Please ensure that you have properly supplied 1 or '
                        'more subregion config values.'
                    )
                    is_well_formed = False


    return is_well_formed

def _contains_unary_metrics(config_metric_data):
    """"""
    unarys = [cls.__name__ for cls in metrics.UnaryMetric.__subclasses__()]
    return any(metric in unarys for metric in config_metric_data)

def _contains_binary_metrics(config_metric_data):
    """"""
    binarys = [cls.__name__ for cls in metrics.BinaryMetric.__subclasses__()]
    return any(metric in binarys for metric in config_metric_data)

def _fetch_built_in_metrics():
    """"""
    unarys = [cls.__name__ for cls in metrics.UnaryMetric.__subclasses__()]
    binarys = [cls.__name__ for cls in metrics.BinaryMetric.__subclasses__()]
    return unarys + binarys

def _valid_dataset_config_data(dataset_config_data):
    """"""
    try:
        data_source = dataset_config_data['data_source']
    except KeyError:
        logger.error('Dataset does not contain a data_source attribute.')
        return False

    if data_source == 'local':
        required_keys = set(['data_source', 'file_count', 'path', 'variable'])
    elif data_source == 'rcmed':
        required_keys = set([
            'dataset_id',
            'parameter_id',
            'min_lat',
            'max_lat',
            'min_lon',
            'max_lon',
            'start_time',
            'end_time',
        ])
    elif data_source == 'esgf':
        required_keys = set([
            'data_source',
            'dataset_id',
            'variable',
            'esgf_username',
            'esgf_password'
        ])
    elif data_source == 'dap':
        required_keys = set({'url', 'variable'})
    else:
        logger.error('Dataset does not contain a valid data_source location.')
        return False

    present_keys = set(dataset_config_data.keys())
    missing_keys = required_keys - present_keys
    contains_required = len(missing_keys) == 0

    if contains_required:
        if data_source == 'local' and dataset_config_data['file_count'] > 1:
            # If the dataset is a multi-file dataset then we need to make sure
            # that the file glob pattern is included.
            if not 'file_glob_pattern' in dataset_config_data:
                logger.error(
                    'Multi-file local dataset is missing key: file_glob_pattern'
                )
                return False
        return True
    else:
        missing = sorted(list(missing_keys))
        logger.error(
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        return False

def _valid_plot_config_data(plot_config_data):
    """"""
    try:
        plot_type = plot_config_data['type']
    except KeyError:
        logger.error('Plot config does not include a type attribute.')
        return False

    if plot_type == 'contour':
        required_keys = set([
            'results_indices',
            'lats',
            'lons',
            'output_name'
        ])
    elif plot_type == 'taylor':
        required_keys = set([
            'stddev_results_indices',
            'pattern_corr_results_indices',
            'output_name'
        ])
    elif plot_type == 'subregion':
        required_keys = set([
            'lats',
            'lons',
            'output_name'
        ])
    elif plot_type == 'time_series':
        required_keys = set([
            'temporal_boundaries'
        ])
    elif plot_type == 'portrait':
        required_keys = set([
            'metric_index',
            'output_name'
        ])
    else:
        logger.error('Invalid plot type specified.')
        return False

    present_keys = set(plot_config_data.keys())
    missing_keys = required_keys - present_keys
    contains_required = len(missing_keys) == 0

    if not contains_required:
        missing = sorted(list(missing_keys))
        logger.error(
            'Plot config does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        return False

    return True

def _valid_subregion_config_data(subregion_config_data):
    """"""
    if type(subregion_config_data) != type([]):
        logger.error(
            'Subregions should be passed as a list of lists where '
            'each sub-list contains a bounding box of the form: '
            '[lat_min, lat_max, lon_min, lon_max].'
        )
        return False

    if len(subregion_config_data) != 4:
        logger.error(
            'Subregions should be passed as a list of lists where '
            'each sub-list contains a bounding box of the form: '
            '[lat_min, lat_max, lon_min, lon_max].'
        )
        return False

    return True
