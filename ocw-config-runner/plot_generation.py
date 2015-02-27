import logging

import ocw.plotter as plots

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
