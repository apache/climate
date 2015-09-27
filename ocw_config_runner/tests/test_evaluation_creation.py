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
