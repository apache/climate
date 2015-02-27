from mock import patch
import unittest

import evaluation_creation as eval_create
import ocw.metrics

import yaml


class TestMetricLoad(unittest.TestCase):
    def test_valid_metric_load(self):
        config = yaml.load("""
            metrics:
                - Bias
        """)
        loaded_metrics = [eval_create._load_metric(m)()
                          for m in config['metrics']]
        self.assertTrue(isinstance(loaded_metrics[0], ocw.metrics.Bias))

    @patch('evaluation_creation.logger')
    def test_invalid_metric_load(self, mock_logger):
        config = yaml.load("""
            metrics:
                - ocw.metrics.Bias
        """)
        eval_create._load_metric(config['metrics'][0])
        error = (
            'User-defined metrics outside of the ocw.metrics module '
            'cannot currently be loaded. If you just wanted a metric '
            'found in ocw.metrics then do not specify the full '
            'package and module names. See the documentation for examples.'
        )
        mock_logger.error.assert_called_with(error)
