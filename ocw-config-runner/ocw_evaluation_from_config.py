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

import argparse
import dateutil.parser
from datetime import timedelta
import logging
import re
import sys

from ocw.dataset import Bounds
from ocw.evaluation import Evaluation
import ocw.metrics as metrics
import ocw.plotter as plots
import ocw.dataset_processor as dsp
import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.data_source.esgf as esgf
import ocw.data_source.dap as dap

import numpy as np
import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)

def run_evaluation_from_config(config_file_path):
    """ Run an OCW evaluation specified by a config file.

    :param config_file_path: The file path to a OCW compliant YAML file
        specifying how to run the evaluation. For additional information on 
        the valid options that you can set in the config please check the
        project wiki https://cwiki.apache.org/confluence/display/climate/home#'.
    :type config_file_path: :mod:`string`
    """
    config = yaml.load(open(config_file_path, 'r'))

    if not is_config_valid(config):
        logger.warning(
            'Unable to validate configuration file. Exiting evaluation. '
            'Please check documentation for config information.'
        )
        sys.exit(1)

    evaluation = generate_evaluation_from_config(config)
    evaluation.run()

    plot_from_config(evaluation, config)

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

def generate_evaluation_from_config(config_data):
    """ Generate an Evaluation object from configuration data.

    :param config_data: Dictionary of the data parsed from the supplied YAML
        configuration file.
    :type config_data: :func:`dict`

    :returns: An Evaluation object containing the data specified in the
        supplied configuration data.
    """
    # Load datasets
    reference = None
    targets = None
    if 'reference' in config_data['datasets']:
        reference = _load_dataset(config_data['datasets']['reference'])

    if 'targets' in config_data['datasets']:
        targets = [_load_dataset(t) for t in config_data['datasets']['targets']]

    reference, targets = _prepare_datasets_for_evaluation(reference,
                                                          targets,
                                                          config_data)
    # Load metrics
    eval_metrics = [_load_metric(m)() for m in config_data['metrics']]

    return Evaluation(reference, targets, eval_metrics)

def plot_from_config(evaluation, config_data):
    """ Generate plots for an evaluation from configuration data.

    :param evaluation: The Evaluation for which to generate plots.
    :type evaluation: :class:`ocw.evaluation.Evaluation`
    :param config_data: Dictionary of the data parsed from the supplied YAML
        configuration file.
    :type: :func:`dict`
    """
    for plot in config_data['plots']:
        if plot['type'] == 'contour':
            _draw_contour_plot(evaluation, plot)
        elif plot['type'] == 'subregion':
            logger.warn('Subregion plots are currently unsupported. Skipping ...')
            continue
        elif plot['type'] == 'taylor':
            logger.warn('Taylor diagrams are currently unsupported. Skipping ...')
            continue
        elif plot['type'] == 'time_series':
            logger.warn('Time series plots are currently unsupported. Skipping ...')
            continue
        elif plot['type'] == 'portrait':
            logger.warn('Portrait diagrams are currently unsupported. Skipping ...')
            continue
        else:
            logger.error('Unrecognized plot type requested: {}'.format(plot['type']))
            continue

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

    if 'plots' in config_data:
        for plot in config_data['plots']:
            if not _valid_plot_config_data(plot):
                is_well_formed = False

    return is_well_formed

def _contains_unary_metrics(config_metric_data):
    """"""
    unarys = [cls.__name__ for cls in metrics.UnaryMetric.__subclasses__()]
    return any(metric in unarys for metric in config_metric_data)

    return True

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
                'results_indeces',
                'lats',
                'lons',
                'output_name'
        ])
    elif plot_type == 'taylor':
        logger.warn('Taylor diagrams are currently unsupported. Skipping validation')
    elif plot_type == 'subregion':
        logger.warn('Subregion plots are currently unsupported. Skipping validation')
    elif plot_type == 'time_series':
        logger.warn('Time series plots are currently unsupported. Skipping validation')
    elif plot_type == 'portrait':
        logger.warn('Portrait diagrams are currently unsupported. Skipping validation')
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

def _load_dataset(dataset_config_data):
    """"""
    if dataset_config_data['data_source'] == 'local':
        if dataset_config_data['file_count'] > 1:
            logger.error(
                'Multi-file datasets are currently not supported. Cancelling load '
                'of the following dataset: {}'.format(dataset_config_data)
            )
            return None

        return local.load_file(dataset_config_data['path'],
                               dataset_config_data['variable'],
                               **dataset_config_data.get('optional_args', {}))
    elif dataset_config_data['data_source'] == 'rcmed':
        return rcmed.parameter_dataset(dataset_config_data['dataset_id'],
                                       dataset_config_data['parameter_id'],
                                       dataset_config_data['min_lat'],
                                       dataset_config_data['max_lat'],
                                       dataset_config_data['min_lon'],
                                       dataset_config_data['min_lon'],
                                       dataset_config_data['start_time'],
                                       dataset_config_data['end_time'],
                                       **dataset_config_data.get('optional_args', {}))
    elif dataset_config_data['data_source'] == 'esgf':
        return esgf.load_dataset(dataset_config_data['dataset_id'],
                                 dataset_config_data['variable'],
                                 dataset_config_data['esgf_username'],
                                 dataset_config_data['esgf_password'],
                                 **dataset_config_data.get('optional_args', {}))
    elif dataset_config_data['data_source'] == 'dap':
        return dap.load(dataset_config_data['url'],
                        dataset_config_data['variable'],
                        **dataset_config_data('optional_args', {}))

def _prepare_datasets_for_evaluation(reference, target, config_data):
    """"""
    subset = config_data['evaluation'].get('subset', None)
    temporal_time_delta = config_data['evaluation'].get('temporal_time_delta', None)
    spatial_regrid_lats = config_data['evaluation'].get('spatial_regrid_lats', None)
    spatial_regrid_lons = config_data['evaluation'].get('spatial_regrid_lons', None)

    if subset:
        start = dateutil.parser.parse(subset[4])
        end = dateutil.parser.parse(subset[5])
        bounds = Bounds(subset[0], subset[1], subset[2], subset[3], start, end)

        if reference:
            reference = dsp.safe_subset(bounds, reference)

        if targets:
            targets = [dsp.safe_subset(bounds, t) for t in targets]

    if temporal_time_delta:
        resolution = timedelta(temporal_time_delta)

        if reference:
            reference = dsp.temporal_rebin(reference, resolution)

        if targets:
            targets = [dsp.temporal_rebin(t, resolution) for t in targets]

    if spatial_regrid_lats and spatial_regrid_lons:
        lats = np.arange(spatial_regrid_lats[0], spatial_regrid_lats[1], spatial_regrid_lats[2])
        lons = np.arange(spatial_regrid_lons[0], spatial_regrid_lons[1], spatial_regrid_lons[2])

        if reference:
            reference = dsp.spatial_regrid(reference, lats, lons)

        if targets:
            targets = [dsp.spatial_regrid(t, lats, lons) for t in targets]

    return reference, target


def _load_metric(metric_config_data):
    """"""
    # If the dataset is user defined outside of ocw.metrics we won't currently
    # handle loading it.
    if '.' in metric_config_data:
        logger.error(
            'User-defined metrics outside of the ocw.metrics module '
            'cannot currently be loaded. If you just wanted a metric '
            'found in ocw.metrics then do not specify the full '
            'package and module names. See the documentation for examples.'
        )
        return None

    return getattr(metrics, metric_config_data)

def _draw_contour_plot(evaluation, plot_config):
    """"""
    row, col = plot_config['results_indeces'][0]

    lats = plot_config['lats']
    if type(lats) != type(list):
        lats = range(lats['range_min'], lats['range_max'], lats['range_step'])

    lons = plot_config['lons']
    if type(lons) != type(list):
        lons = range(lons['range_min'], lons['range_max'], lons['range_step'])

    plots.draw_contour_map(evaluation.results[row][col],
                            np.array(lats),
                            np.array(lons),
                            plot_config['output_name'],
                            **plot_config.get('optional_args', {}))

if __name__ == '__main__':
    description = 'OCW Config Based Evaluation'
    epilog = 'Additional information at https://cwiki.apache.org/confluence/display/climate/home#'

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('config', help='Path to YAML config file for the evaluation')
    args = parser.parse_args()

    run_evaluation_from_config(args.config)
