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

import ocw_config_runner.configuration_parsing as parser
import ocw.metrics as metrics

import yaml


class TestIsConfigValid(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        not_minimal_config = """
            datasets:
        """
        self.not_minimal = yaml.load(not_minimal_config)

        not_well_formed_config = """
        datasets:
            reference:
                data_source: local
                file_count: 1
                path: /a/fake/path/file.py
                variable: pr

            targets:
                - data_source: local
                  file_count: 5
                  file_glob_pattern: something for globbing files here
                  variable: pr
                  optional_args:
                      name: Target1

                - data_source: esgf
                  dataset_id: fake dataset id
                  variable: pr
                  esgf_username: my esgf username
                  esgf_password: my esgf password

        metrics:
            - Bias
            - TemporalStdDev
        """
        self.not_well_formed = yaml.load(not_well_formed_config)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_not_minimal_config(self, mock_logger):
        ret = parser.is_config_valid(self.not_minimal)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Insufficient configuration file data for an evaluation'
        )

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_not_valid_config(self, mock_logger):
        ret = parser.is_config_valid(self.not_well_formed)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Configuration data is not well formed'
        )


class TestValidMinimalConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        no_datasets_config = """
        metrics:
            - Bias
        """
        self.no_datasets = yaml.load(no_datasets_config)

        no_metrics_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr
        """
        self.no_metrics = yaml.load(no_metrics_config)

        unary_with_reference_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_with_reference = yaml.load(unary_with_reference_config)

        unary_with_target_config = """
        datasets:
            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_with_target = yaml.load(unary_with_target_config)

        unary_no_reference_or_target = """
        datasets:
            not_ref_or_target:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_no_ref_or_target = yaml.load(unary_no_reference_or_target)

        binary_valid_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr
        metrics:
            - Bias
        """
        self.binary_valid = yaml.load(binary_valid_config)

        binary_no_reference_config = """
        datasets:
            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr
        metrics:
            - Bias
        """
        self.binary_no_reference = yaml.load(binary_no_reference_config)

        binary_no_target_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

        metrics:
            - Bias
        """
        self.binary_no_target = yaml.load(binary_no_target_config)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_no_datasets(self, mock_logger):
        ret = parser._valid_minimal_config(self.no_datasets)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'No datasets specified in configuration data.'
        )

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_no_metrics(self, mock_logger):
        ret = parser._valid_minimal_config(self.no_metrics)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'No metrics specified in configuration data.'
        )

    def test_unary_with_reference(self):
        ret = parser._valid_minimal_config(self.unary_with_reference)
        self.assertTrue(ret)

    def test_unary_with_target(self):
        ret = parser._valid_minimal_config(self.unary_with_target)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_unary_no_datasets(self, mock_logger):
        ret = parser._valid_minimal_config(self.unary_no_ref_or_target)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Unary metric in configuration data requires either a reference '
            'or target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )

    def test_valid_binary(self):
        ret = parser._valid_minimal_config(self.binary_valid)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_binary_no_reference(self, mock_logger):
        ret = parser._valid_minimal_config(self.binary_no_reference)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Binary metric in configuration requires both a reference '
            'and target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )
        
    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_binary_no_target(self, mock_logger):
        ret = parser._valid_minimal_config(self.binary_no_target)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Binary metric in configuration requires both a reference '
            'and target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )


class TestConfigIsWellFormed(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        malformed_reference_config = """
            datasets:
                reference:
                    data_source: notavalidlocation

            metrics:
                - Bias
        """
        self.malformed_reference_conf = yaml.load(malformed_reference_config)

        malformed_target_list_config = """
            datasets:
                targets:
                    notalist: 
                        a_key: a_value

                    alsonotalist:
                        a_key: a_value

            metrics:
                - Bias
        """
        self.malformed_target_list = yaml.load(malformed_target_list_config)

        missing_metric_name_config = """
            datasets:
                reference:
                    data_source: dap
                    url: afakeurl.com
                    variable: pr

            metrics:
                - NotABuiltInMetric
        """
        self.missing_metric_name = yaml.load(missing_metric_name_config)

        bad_plot_config = """
            datasets:
                reference:
                    data_source: dap
                    url: afakeurl.com
                    variable: pr

            metrics:
                - Bias

            plots:
                - type: NotARealPlotName
        """
        bad_plot = yaml.load(bad_plot_config)

        bad_subregion_config_type = """
            datasets:
                reference:
                    data_source: dap
                    url: afakeurl.com
                    variable: pr

            metrics:
                - Bias

            subregions:
                - this is a string instead of a list
        """
        self.bad_subregion_type = yaml.load(bad_subregion_config_type)

        bad_subregion_config_length = """
            datasets:
                reference:
                    data_source: dap
                    url: afakeurl.com
                    variable: pr

            metrics:
                - Bias

            subregions:
                - [1, 2, 3, 4, 5]
        """
        self.bad_subregion_length = yaml.load(bad_subregion_config_length)

    def test_malformed_reference_config(self):
        ret = parser._config_is_well_formed(self.malformed_reference_conf)
        self.assertFalse(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_malformed_target_dataset_list(self, mock_logger):
        ret = parser._config_is_well_formed(self.malformed_target_list)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            "Expected to find list of target datasets but instead found "
            "object of type <type 'dict'>"
        )

    def test_not_builtin_metric(self):
        ret = parser._config_is_well_formed(self.missing_metric_name)
        self.assertFalse(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_warns_regarding_not_builtin_metric(self, mock_logger):
        ret = parser._config_is_well_formed(self.missing_metric_name)
        mock_logger.warn.assert_called_with(
            'Unable to locate metric name NotABuiltInMetric in built-in '
            'metrics. If this is not a user defined metric then please check '
            'for potential misspellings.'
        )

    def test_bad_plot_config(self):
        ret = parser._config_is_well_formed(self.missing_metric_name)
        self.assertFalse(ret)
    
    def test_bad_subregion_type(self):
        ret = parser._config_is_well_formed(self.bad_subregion_type)
        self.assertFalse(ret)

    def test_bad_subregion_length(self):
        ret = parser._config_is_well_formed(self.bad_subregion_length)
        self.assertFalse(ret)


class MetricFetchTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        binary_config = """
            metrics:
                - Bias
                - StdDevRatio
        """
        unary_config = """
            metrics:
                - TemporalStdDev
        """
        self.unary_conf = yaml.load(unary_config)
        self.binary_conf = yaml.load(binary_config)

    def test_contains_binary_metric(self):
        ret = parser._contains_binary_metrics(self.binary_conf['metrics'])
        self.assertTrue(ret)

    def test_does_not_contain_binary_metric(self):
        ret = parser._contains_binary_metrics(self.unary_conf['metrics'])
        self.assertFalse(ret)

    def test_contains_unary_metric(self):
        ret = parser._contains_unary_metrics(self.unary_conf['metrics'])
        self.assertTrue(ret)
        
    def test_does_not_contain_unary_metric(self):
        ret = parser._contains_unary_metrics(self.binary_conf['metrics'])
        self.assertFalse(ret)


class InvalidDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        example_config_yaml = """
            - file_count: 1
              path: /a/fake/path
              variable: pr

            - data_source: invalid_location_identifier
        """
        conf = yaml.load(example_config_yaml)
        self.missing_data_source = conf[0]
        self.invalid_data_source = conf[1]

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_missing_data_source_config(self, mock_logger):
        parser._valid_dataset_config_data(self.missing_data_source)
        mock_logger.error.assert_called_with(
            'Dataset does not contain a data_source attribute.'
        )

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_data_source(self, mock_logger):
        parser._valid_dataset_config_data(self.invalid_data_source)
        mock_logger.error.assert_called_with(
            'Dataset does not contain a valid data_source location.'
        )


class TestLocalDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_local_keys = set(['data_source', 'file_count', 'path', 'variable'])
        example_config_yaml = """
            - data_source: local
              file_count: 1
              path: /a/fake/path
              variable: pr
              optional_args:
                  name: Target1

            - data_source: local

            - data_source: local
              file_count: 5
              file_glob_pattern: something for globbing files here
              variable: pr
              path: /a/fake/path
              optional_args:
                  name: Target1

            - data_source: local
              file_count: 5
              variable: pr
              path: /a/fake/path
        """

        conf = yaml.load(example_config_yaml)
        self.valid_local_single = conf[0]
        self.invalid_local_single = conf[1]
        self.valid_local_multi = conf[2]
        self.invalid_local_multi = conf[1]
        self.invalid_local_multi_file_glob = conf[3]

    def test_valid_local_config_single_file(self):
        ret = parser._valid_dataset_config_data(self.valid_local_single)
        self.assertTrue(ret)

    def test_valid_local_config_multi_file(self):
        ret = parser._valid_dataset_config_data(self.valid_local_multi)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_local_config(self, mock_logger):
        parser._valid_dataset_config_data(self.invalid_local_single)

        present_keys = set(self.invalid_local_single.keys())
        missing_keys = self.required_local_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_local_config_multi_file(self, mock_logger):
        # mutlifile config is handled slightly differently. We should see the
        # same missing keys in this situation as we would on the single file
        # local config. We will test for a missing file_glob_pattern in a
        # different test.
        parser._valid_dataset_config_data(self.invalid_local_multi)

        present_keys = set(self.invalid_local_multi.keys())
        missing_keys = self.required_local_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_local_config_multi_file_missing_file_glob(self, mock_logger):
        # We can't check for the file_glob_pattern pattern until after we have
        # verified that the single local file config has been met.
        parser._valid_dataset_config_data(self.invalid_local_multi_file_glob)

        mock_logger.error.assert_called_with(
            'Multi-file local dataset is missing key: file_glob_pattern'
        )


class TestRCMEDDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_rcmed_keys = set([
            'dataset_id',
            'parameter_id',
            'min_lat',
            'max_lat',
            'min_lon',
            'max_lon',
            'start_time',
            'end_time'
        ])
        example_config_yaml = """
            - data_source: rcmed
              dataset_id: 4
              parameter_id: 4
              min_lat: -40
              max_lat: 40
              min_lon: -50
              max_lon: 50
              start_time: YYYY-MM-DDThh:mm:ss
              end_time: YYYY-MM-DDThh:mm:ss

            - data_source: rcmed
        """
        conf = yaml.load(example_config_yaml)
        self.valid_rcmed = conf[0]
        self.invalid_rcmed = conf[1]

    def test_valid_rcmed_config(self):
        ret = parser._valid_dataset_config_data(self.valid_rcmed)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_rcmed_config(self, mock_logger):
        parser._valid_dataset_config_data(self.invalid_rcmed)

        present_keys = set(self.invalid_rcmed.keys())
        missing_keys = self.required_rcmed_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class TestESGFDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_esgf_keys = set([
            'data_source',
            'dataset_id',
            'variable',
            'esgf_username',
            'esgf_password'
        ])
        example_config_yaml = """
           - data_source: esgf
             dataset_id: fake dataset id
             variable: pr
             esgf_username: my esgf username
             esgf_password: my esgf password

           - data_source: esgf
        """
        conf = yaml.load(example_config_yaml)
        self.valid_esgf = conf[0]
        self.invalid_esgf = conf[1]

    def test_valid_esgf_conf(self):
        ret = parser._valid_dataset_config_data(self.valid_esgf)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_esgf_conf(self, mock_logger):
        parser._valid_dataset_config_data(self.invalid_esgf)

        present_keys = set(self.invalid_esgf.keys())
        missing_keys = self.required_esgf_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class TestDAPDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_dap_keys = set(['url', 'variable'])
        example_config_yaml = """
           - data_source: dap
             url: afakeurl.com
             variable: pr

           - data_source: dap
        """
        conf = yaml.load(example_config_yaml)
        self.valid_dap = conf[0]
        self.invalid_dap = conf[1]

    def test_valid_dap_config(self):
        ret = parser._valid_dataset_config_data(self.valid_dap)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_dap_config(self, mock_logger):
        parser._valid_dataset_config_data(self.invalid_dap)

        present_keys = set(self.invalid_dap.keys())
        missing_keys = self.required_dap_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class ContourMapConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        valid_contour_config = """
            type: contour
            results_indices:
                - !!python/tuple [0, 0]
            lats:
                range_min: -20
                range_max: 20
                range_step: 1
            lons:
                range_min: -20
                range_max: 20
                range_step: 1
            output_name: wrf_bias_compared_to_knmi
        """
        self.valid_contour = yaml.load(valid_contour_config)

        missing_keys_contour_config = """
            type: contour
        """
        self.missing_keys_contour = yaml.load(missing_keys_contour_config)

        self.required_contour_keys = set([
            'results_indices',
            'lats',
            'lons',
            'output_name'
        ])

    def test_valid_contour(self):
        ret = parser._valid_plot_config_data(self.valid_contour)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_missing_keys_contour(self, mock_logger):
        ret = parser._valid_plot_config_data(self.missing_keys_contour)

        present_keys = set(self.missing_keys_contour.keys())
        missing_keys = self.required_contour_keys - present_keys
        missing = sorted(list(missing_keys))

        err = (
            'Plot config does not contain required keys. '
            'The following keys are missing: {}'
        ).format(', '.join(missing))
        mock_logger.error.assert_called_with(err)


class TestSubregionPlotConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        valid_subregion_config = """
            type: subregion
            lats:
                range_min: -20
                range_max: 20
                range_step: 1
            lons:
                range_min: -20
                range_max: 20
                range_step: 1
            output_name: fake_plot_name
        """
        self.valid_subregion = yaml.load(valid_subregion_config)

        missing_keys_subregion_config = """
            type: subregion
        """
        self.missing_keys_subregion = yaml.load(missing_keys_subregion_config)

        self.required_subregion_keys = set([
            'lats',
            'lons',
            'output_name'
        ])

    def test_valid_subregion(self):
        ret = parser._valid_plot_config_data(self.valid_subregion)
        self.assertTrue(ret)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_missing_keys_subregion(self, mock_logger):
        ret = parser._valid_plot_config_data(self.missing_keys_subregion)

        present_keys = set(self.missing_keys_subregion.keys())
        missing_keys = self.required_subregion_keys - present_keys
        missing = sorted(list(missing_keys))

        err = (
            'Plot config does not contain required keys. '
            'The following keys are missing: {}'
        ).format(', '.join(missing))
        mock_logger.error.assert_called_with(err)


class TestInvalidPlotConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        bad_plot_type_config = """
            type: NotAPlotType
        """
        self.bad_plot_type = yaml.load(bad_plot_type_config)

        missing_plot_type_config = """
            results_indices:
                - !!python/tuple [0, 0]
            lats:
                range_min: -20
                range_max: 20
                range_step: 1
            lons:
                range_min: -20
                range_max: 20
                range_step: 1
            output_name: wrf_bias_compared_to_knmi
        """
        self.missing_plot_type = yaml.load(missing_plot_type_config)

        missing_subregions_for_plot_type = """
            datasets:
                - blah

            metrics:
                - blah
            
            plots:
                - type: subregion
                  results_indices:
                      - !!python/tuple [0, 0]
                  lats:
                      range_min: -20
                      range_max: 20
                      range_step: 1
                  lons:
                      range_min: -20
                      range_max: 20
                      range_step: 1
                  output_name: wrf_bias_compared_to_knmi
        """
        self.missing_subregions = yaml.load(missing_subregions_for_plot_type)

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_invalid_plot_type(self, mock_logger):
        ret = parser._valid_plot_config_data(self.bad_plot_type)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Invalid plot type specified.'
        )

    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_missing_plot_type(self, mock_logger):
        ret = parser._valid_plot_config_data(self.missing_plot_type)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Plot config does not include a type attribute.'
        )
        
    @patch('ocw_config_runner.configuration_parsing.logger')
    def test_missing_subregion(self, mock_logger):
        ret = parser._config_is_well_formed(self.missing_subregions)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Plot config that requires subregion information is present '
            'in a config file without adequate subregion information '
            'provided. Please ensure that you have properly supplied 1 or '
            'more subregion config values.'
        )
