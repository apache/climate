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

import ocw.dataset_processor as dsp
import ocw.plotter as plots
import ocw.utils as utils

import numpy as np

logging.basicConfig()
logger = logging.getLogger(__name__)

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
            _draw_subregion_diagram(evaluation, plot)
        elif plot['type'] == 'taylor':
            _draw_taylor_diagram(evaluation, plot)
        elif plot['type'] == 'time_series':
            _draw_time_series_plot(evaluation, plot)
        elif plot['type'] == 'portrait':
            _draw_portrait_diagram(evaluation, plot)
        else:
            logger.error('Unrecognized plot type requested: {}'.format(plot['type']))

def _draw_contour_plot(evaluation, plot_config):
    """"""
    lats = plot_config['lats']
    if type(lats) != type(list):
        lats = np.arange(lats['range_min'], lats['range_max'], lats['range_step'])

    lons = plot_config['lons']
    if type(lons) != type(list):
        lons = np.arange(lons['range_min'], lons['range_max'], lons['range_step'])

    for i, index in enumerate(plot_config['results_indices']):
        if len(index) == 2:
            target, metric = index
            vals = evaluation.results[target][metric]
        elif len(index) == 3:
            target, metric, subregion = index
            vals = evaluation.results[target][metric][subregion]

        plot_name = plot_config['output_name'] + '_{}'.format(i)
        plots.draw_contour_map(vals,
                               np.array(lats),
                               np.array(lons),
                               plot_name,
                               **plot_config.get('optional_args', {}))

def _draw_taylor_diagram(evaluation, plot_config):
    """"""
    plot_name = plot_config['output_name']
    ref_dataset_name = evaluation.ref_dataset.name
    target_dataset_names = [t.name for t in evaluation.target_datasets]

    if len(plot_config['stddev_results_indices'][0]) == 2:
        stddev_results = [
            evaluation.results[tar][met]
            for (tar, met) in plot_config['stddev_results_indices']
        ]

        pattern_corr_results = [
            evaluation.results[tar][met]
            for (tar, met) in plot_config['pattern_corr_results_indices']
        ]
    elif len(plot_config['stddev_results_indices'][0]) == 3:
        stddev_results = [
            evaluation.results[tar][met][sub]
            for (tar, met, sub) in plot_config['stddev_results_indices']
        ]

        pattern_corr_results = [
            evaluation.results[tar][met][sub]
            for (tar, met, sub) in plot_config['pattern_corr_results_indices']
        ]

    plot_data = np.array([stddev_results, pattern_corr_results]).transpose()

    plots.draw_taylor_diagram(plot_data,
                              target_dataset_names,
                              ref_dataset_name,
                              fname=plot_name,
                              **plot_config.get('optional_args', {}))

def _draw_subregion_diagram(evaluation, plot_config):
    """"""
    lats = plot_config['lats']
    if type(lats) != type(list):
        lats = np.arange(lats['range_min'], lats['range_max'], lats['range_step'])

    lons = plot_config['lons']
    if type(lons) != type(list):
        lons = np.arange(lons['range_min'], lons['range_max'], lons['range_step'])

    plots.draw_subregions(evaluation.subregions,
                          lats,
                          lons,
                          plot_config['output_name'],
                          **plot_config.get('optional_args', {}))

def _draw_portrait_diagram(evaluation, plot_config):
    """"""
    metric_index = plot_config['metric_index']

    diagram_data = np.array(evaluation.results[:][metric_index][:])
    subregion_names = ["R{}".format(i) for i in range(len(evaluation.subregions))]
    target_names = [t.name for t in evaluation.target_datasets]

    plots.draw_portrait_diagram(diagram_data,
                                target_names,
                                subregion_names,
                                fname=plot_config['output_name'],
                                **plot_config.get('optional_args', {}))

def _draw_time_series_plot(evaluation, plot_config):
    """"""
    temporal_boundaries_info = plot_config['temporal_boundaries']
    ref_ds = evaluation.ref_dataset
    target_ds = evaluation.target_datasets

    if temporal_boundaries_info == 'monthly':
        ref_ds.values, ref_ds.times = utils.calc_climatology_monthly(ref_ds)

        for t in target_ds:
            t.values, t.times = utils.calc_climatology_monthly(t)
    else:
        logger.error(
            'Invalid time range provided. Only monthly is supported '
            'at the moment'
        )
        return

    if evaluation.subregions:
        for bound_count, bound in enumerate(evaluation.subregions):
            results = []
            labels = []

            subset = dsp.subset(
                ref_ds,
                bound,
                subregion_name="R{}_{}".format(bound_count, ref_ds.name)
            )

            results.append(utils.calc_time_series(subset))
            labels.append(subset.name)

            for t in target_ds:
                subset = dsp.subset(
                    t,
                    bound,
                    subregion_name="R{}_{}".format(bound_count, t.name)
                )
                results.append(utils.calc_time_series(subset))
                labels.append(subset.name)

            plots.draw_time_series(np.array(results),
                                   ref_ds.times,
                                   labels,
                                   'R{}'.format(bound_count),
                                   **plot_config.get('optional_args', {}))

    else:
        results = []
        labels = []

        results.append(utils.calc_time_series(ref_ds))
        labels.append(ref_ds.name)

        for t in target_ds:
            results.append(utils.calc_time_series(t))
            labels.append(t.name)

        plots.draw_time_series(np.array(results),
                               ref_ds.times,
                               labels,
                               'time_series',
                               **plot_config.get('optional_args', {}))
