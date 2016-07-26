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

import dateutil.parser
from datetime import timedelta
import logging

from ocw.dataset import Bounds
from ocw.evaluation import Evaluation
import ocw.dataset_processor as dsp
import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.data_source.esgf as esgf
import ocw.data_source.dap as dap
import ocw.metrics as metrics

import numpy as np

logging.basicConfig()
logger = logging.getLogger(__name__)

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
    targets = []
    if config_data['datasets']:
        if 'reference' in config_data['datasets']:
            reference = _load_dataset(config_data['datasets']['reference'])

        if 'targets' in config_data['datasets']:
            targets = [_load_dataset(t) for t in config_data['datasets']['targets']]

        reference, targets = _prepare_datasets_for_evaluation(reference,
                                                              targets,
                                                              config_data)
    # Load metrics
    eval_metrics = []
    if config_data['metrics']:
        eval_metrics = [_load_metric(m)() for m in config_data['metrics']]

    # Load Subregions (if present)
    subregions = None
    if 'subregions' in config_data:
        subregions = [_load_subregion(s) for s in config_data['subregions']]

    return Evaluation(reference, targets, eval_metrics, subregions=subregions)

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

def _prepare_datasets_for_evaluation(reference, targets, config_data):
    """"""
    subset = config_data['evaluation'].get('subset', None)
    temporal_time_delta = config_data['evaluation'].get('temporal_time_delta', None)
    spatial_regrid_lats = config_data['evaluation'].get('spatial_regrid_lats', None)
    spatial_regrid_lons = config_data['evaluation'].get('spatial_regrid_lons', None)

    # If we have a temporal time delta and it's daily (i.e., 1) we will
    # normalize the data as daily data (which means we adjust the start times
    # for each bucket of data to be consistent). By default we will normalize
    # the data as monthly. Note that this will not break yearly data so it's
    # safer to do this no matter what. This keeps us from ending up with 1-off
    # errors in the resulting dataset shape post-temporal/spatial adjustments
    # that break evaluations.
    string_time_delta = 'monthly'
    if temporal_time_delta and temporal_time_delta == 1:
        string_time_delta = 'daily'

    reference = dsp.normalize_dataset_datetimes(reference, string_time_delta)
    targets = [dsp.normalize_dataset_datetimes(t, string_time_delta) for t in targets]

    if subset:
        start = dateutil.parser.parse(subset[4])
        end = dateutil.parser.parse(subset[5])
        bounds = Bounds(subset[0], subset[1], subset[2], subset[3], start, end)

        if reference:
            reference = dsp.safe_subset(reference, bounds)

        if targets:
            targets = [dsp.safe_subset(t, bounds) for t in targets]

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

    return reference, targets

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

def _load_subregion(subregion_config_data):
    """"""
    return Bounds(float(subregion_config_data[0]),
                  float(subregion_config_data[1]),
                  float(subregion_config_data[2]),
                  float(subregion_config_data[3]))
