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
import os
import unittest

from ocw.dataset import Dataset, Bounds
from ocw.evaluation import Evaluation
import ocw.metrics as metrics
import ocw_config_runner.configuration_writer as writer

import datetime as dt
import numpy as np
import yaml


class TestLocalDatasetExportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.origin = {
            'source': 'local',
            'path': '/a/fake/path.nc',
            'lat_name': 'a lat name',
            'lon_name': 'a lon name',
            'time_name': 'a time name',
            'elevation_index': 2
        }
        self.name = 'name'

        self.dataset = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            origin=self.origin,
            name=self.name
        )

        self.exported_info = writer.generate_dataset_config(self.dataset)

    def test_proper_data_source_export(self):
        self.assertTrue('data_source' in self.exported_info)
        self.assertEqual(self.exported_info['data_source'],
                         self.origin['source'])

    def test_proper_path_export(self):
        self.assertEqual(self.exported_info['path'], self.origin['path'])

    def test_proper_variable_name_export(self):
        self.assertEqual(self.exported_info['variable'], self.variable)

    def test_proper_units_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['units'],
                         self.units)

    def test_proper_lats_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['lat_name'],
                         self.origin['lat_name'])

    def test_proper_lons_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['lon_name'],
                         self.origin['lon_name'])

    def test_proper_times_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['time_name'],
                         self.origin['time_name'])

    def test_proper_dataset_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['name'],
                         self.name)

    def test_proper_elevation_index_export(self):
        self.assertEqual(self.exported_info['optional_args']['elevation_index'],
                         self.origin['elevation_index'])


class TestRCMEDDatasetExportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.origin = {
            'source': 'rcmed',
            'dataset_id': 4,
            'parameter_id': 14
        }
        self.name = 'name'

        self.dataset = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            origin=self.origin,
            name=self.name
        )

        self.exported_info = writer.generate_dataset_config(self.dataset)

    def test_proper_data_source_export(self):
        self.assertTrue('data_source' in self.exported_info)
        self.assertEqual(self.exported_info['data_source'],
                         self.origin['source'])

    def test_proper_dataset_id_export(self):
        self.assertEqual(self.exported_info['dataset_id'],
                         self.origin['dataset_id'])

    def test_proper_parameter_id_export(self):
        self.assertEqual(self.exported_info['parameter_id'],
                         self.origin['parameter_id'])

    def test_proper_min_lat_export(self):
        self.assertEqual(self.exported_info['min_lat'], min(self.lats))

    def test_proper_max_lat_export(self):
        self.assertEqual(self.exported_info['max_lat'], max(self.lats))

    def test_proper_min_lon_export(self):
        self.assertEqual(self.exported_info['min_lon'], min(self.lons))

    def test_proper_max_lon_export(self):
        self.assertEqual(self.exported_info['max_lon'], max(self.lons))

    def test_proper_min_time_export(self):
        self.assertEqual(self.exported_info['start_time'], str(min(self.times)))

    def test_proper_max_time_export(self):
        self.assertEqual(self.exported_info['end_time'], str(max(self.times)))

    def test_proper_dataset_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['name'],
                         self.name)

    def test_proper_units_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['units'],
                         self.units)


class TestESGFDatasetExportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.origin = {
            'source': 'esgf',
            'dataset_id': 'esgf dataset id',
            'variable': 'var'
        }
        self.name = 'name'

        self.dataset = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            origin=self.origin,
            name=self.name
        )

        self.exported_info = writer.generate_dataset_config(self.dataset)

    def test_proper_data_source_export(self):
        self.assertTrue('data_source' in self.exported_info)
        self.assertEqual(self.exported_info['data_source'],
                     self.origin['source'])

    def test_proper_dataset_id_export(self):
        self.assertEqual(self.exported_info['dataset_id'],
                         self.origin['dataset_id'])

    def test_proper_variable_export(self):
        self.assertEqual(self.exported_info['variable'],
                         self.origin['variable'])

    def test_proper_dummy_username_export(self):
        self.assertTrue('esgf_username' in self.exported_info)

    def test_proper_dummy_password_export(self):
        self.assertTrue('esgf_password' in self.exported_info)

    def test_proper_dataset_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['name'],
                         self.name)

    def test_proper_units_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['units'],
                         self.units)


class TestDAPDatasetExportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.origin = {
            'source': 'dap',
            'url': 'a fake url',
        }
        self.name = 'name'

        self.dataset = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            origin=self.origin,
            name=self.name
        )

        self.exported_info = writer.generate_dataset_config(self.dataset)

    def test_proper_data_source_export(self):
        self.assertTrue('data_source' in self.exported_info)
        self.assertEqual(self.exported_info['data_source'],
                     self.origin['source'])

    def test_proper_url_export(self):
        self.assertEqual(self.exported_info['url'],
                         self.origin['url'])

    def test_proper_dataset_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['name'],
                         self.name)

    def test_proper_units_name_export(self):
        self.assertEqual(self.exported_info['optional_args']['units'],
                         self.units)


class TestDatasetExportFromEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.name = 'name'

        self.local_origin = {
            'source': 'local',
            'path': '/a/fake/path.nc',
            'lat_name': 'a lat name',
            'lon_name': 'a lon name',
            'time_name': 'a time name',
            'elevation_index': 2
        }

        self.rcmed_origin = {
            'source': 'rcmed',
            'dataset_id': 4,
            'parameter_id': 14
        }

        self.esgf_origin = {
            'source': 'esgf',
            'dataset_id': 'esgf dataset id',
            'variable': 'var'
        }

        self.dap_origin = {
            'source': 'dap',
            'url': 'a fake url',
        }

        self.local_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.local_origin
        )

        self.rcmed_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.rcmed_origin
        )

        self.esgf_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.esgf_origin
        )

        self.dap_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.dap_origin
        )

        self.evaluation = Evaluation(
            self.local_ds,
            [self.rcmed_ds, self.esgf_ds, self.dap_ds],
            []
        )

    def test_contains_only_reference_dataset(self):
        new_eval = Evaluation(self.local_ds, [], [])
        out = writer.generate_dataset_information(new_eval)

        self.assertTrue('reference' in out)
        self.assertTrue('targets' not in out)

    def test_contains_only_target_datasets(self):
        new_eval = Evaluation(None, [self.local_ds], [])
        out = writer.generate_dataset_information(new_eval)

        self.assertTrue('reference' not in out)
        self.assertTrue('targets' in out)

    def test_proper_reference_dataset_export(self):
        out = writer.generate_dataset_information(self.evaluation)

        self.assertTrue('reference' in out)
        self.assertTrue(out['reference']['data_source'] == 'local')

    def test_proper_target_datasets_export(self):
        out = writer.generate_dataset_information(self.evaluation)

        self.assertTrue('targets' in out)
        self.assertTrue(type(out['targets']) == type(list()))
        self.assertTrue(len(out['targets']) == 3)


class TestMetricExportGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.bias = metrics.Bias()
        self.tmp_std_dev = metrics.TemporalStdDev()
        loaded_metrics = [self.bias, self.tmp_std_dev]

        self.evaluation = Evaluation(None, [], loaded_metrics)

    def test_proper_export_format(self):
        out = writer.generate_metric_information(self.evaluation)

        self.assertTrue(type(out) == type(list()))

        for name in out:
            self.assertTrue(type(name) == type(str()))

    def test_proper_metric_name_export(self):
        out = writer.generate_metric_information(self.evaluation)

        self.assertTrue(self.bias.__class__.__name__ in out)
        self.assertTrue(self.tmp_std_dev.__class__.__name__ in out)

    def test_empty_metrics_in_evaluation(self):
        new_eval = Evaluation(None, [], [])
        out = writer.generate_metric_information(new_eval)

        self.assertTrue(type(out) == type(list()))
        self.assertTrue(len(out) == 0)


class TestEvaluationSettingsGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array(range(-10, 10, 1))
        self.lons = np.array(range(-20, 20, 1))
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(9600))
        self.values = flat_array.reshape(12, 20, 40)

        self.dataset = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
        )

        self.evaluation = Evaluation(self.dataset, [], [])

    def test_default_data_return(self):
        new_eval = Evaluation(None, [], [])
        default_output = {
            'temporal_time_delta': 999,
            'spatial_regrid_lats': (-90, 90, 1),
            'spatial_regrid_lons': (-180, 180, 1),
            'subset': [-90, 90, -180, 180, "1500-01-01", "2500-01-01"],
        }

        out = writer.generate_evaluation_information(new_eval)

        self.assertEquals(default_output, out)

    def test_handles_only_reference_dataset(self):
        new_eval = Evaluation(self.dataset, [], [])

        default_output = {
            'temporal_time_delta': 999,
            'spatial_regrid_lats': (-90, 90, 1),
            'spatial_regrid_lons': (-180, 180, 1),
            'subset': [-90, 90, -180, 180, "1500-01-01", "2500-01-01"],
        }

        out = writer.generate_evaluation_information(new_eval)

        self.assertNotEquals(default_output, out)

    def test_handles_only_target_dataset(self):
        new_eval = Evaluation(None, [self.dataset], [])

        default_output = {
            'temporal_time_delta': 999,
            'spatial_regrid_lats': (-90, 90, 1),
            'spatial_regrid_lons': (-180, 180, 1),
            'subset': [-90, 90, -180, 180, "1500-01-01", "2500-01-01"],
        }

        out = writer.generate_evaluation_information(new_eval)

        self.assertNotEquals(default_output, out)

    def test_daily_temporal_bin(self):
        new_times = np.array([dt.datetime(2000, 1, 1, x) for x in range(1, 13)])

        dataset = Dataset(
            self.lats,
            self.lons,
            new_times,
            self.values,
        )
        new_eval = Evaluation(dataset, [], [])

        out = writer.generate_evaluation_information(new_eval)

        self.assertEquals(out['temporal_time_delta'], 1)

    def test_monthly_temporal_bin(self):
        out = writer.generate_evaluation_information(self.evaluation)

        self.assertEquals(out['temporal_time_delta'], 31)

    def test_yearly_temporal_bin(self):
        new_times = np.array([dt.datetime(2000 + x, 1, 1) for x in range(1, 13)])

        dataset = Dataset(
            self.lats,
            self.lons,
            new_times,
            self.values,
        )
        new_eval = Evaluation(dataset, [], [])

        out = writer.generate_evaluation_information(new_eval)

        self.assertEquals(out['temporal_time_delta'], 366)

    def test_spatial_regrid_lats(self):
        out = writer.generate_evaluation_information(self.evaluation)

        lats = out['spatial_regrid_lats']
        lat_range = np.arange(lats[0], lats[1], lats[2])

        self.assertTrue(np.array_equal(lat_range, self.lats))

    def test_spatial_regrid_lons(self):
        out = writer.generate_evaluation_information(self.evaluation)

        lons = out['spatial_regrid_lons']
        lat_range = np.arange(lons[0], lons[1], lons[2])

        self.assertTrue(np.array_equal(lat_range, self.lons))

    def test_subset_with_single_dataset(self):
        out = writer.generate_evaluation_information(self.evaluation)
        subset = out['subset']

        ds_lat_min, ds_lat_max, ds_lon_min, ds_lon_max = self.dataset.spatial_boundaries()
        start, end = self.dataset.time_range()

        self.assertEqual(ds_lat_min, subset[0])
        self.assertEqual(ds_lat_max, subset[1])
        self.assertEqual(ds_lon_min, subset[2])
        self.assertEqual(ds_lon_max, subset[3])
        self.assertEquals(str(start), subset[4])
        self.assertEquals(str(end), subset[5])

    def test_subset_with_multiple_datasets(self):
        new_ds = Dataset(
            np.arange(0, 20, 1),
            self.lons,
            self.times,
            self.values
        )
        new_eval = Evaluation(self.dataset, [new_ds], [])

        out = writer.generate_evaluation_information(new_eval)
        subset = out['subset']

        ds_lat_min, ds_lat_max, ds_lon_min, ds_lon_max = self.dataset.spatial_boundaries()
        start, end = self.dataset.time_range()

        self.assertEqual(ds_lat_min, subset[0])
        # Check that we actually used the different max lat value that we
        # created by adding 'new_ds'.
        self.assertEqual(max(new_ds.lats), subset[1])
        self.assertEqual(ds_lon_min, subset[2])
        self.assertEqual(ds_lon_max, subset[3])
        self.assertEquals(str(start), subset[4])
        self.assertEquals(str(end), subset[5])


class FullExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.lats = np.array([10, 12, 14, 16, 18])
        self.lons = np.array([100, 102, 104, 106, 108])
        self.times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.values = flat_array.reshape(12, 5, 5)
        self.variable = 'var'
        self.units = 'units'
        self.name = 'name'

        self.local_origin = {
            'source': 'local',
            'path': '/a/fake/path.nc',
            'lat_name': 'a lat name',
            'lon_name': 'a lon name',
            'time_name': 'a time name',
            'elevation_index': 2
        }

        self.rcmed_origin = {
            'source': 'rcmed',
            'dataset_id': 4,
            'parameter_id': 14
        }

        self.esgf_origin = {
            'source': 'esgf',
            'dataset_id': 'esgf dataset id',
            'variable': 'var'
        }

        self.dap_origin = {
            'source': 'dap',
            'url': 'a fake url',
        }

        self.local_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.local_origin
        )

        self.rcmed_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.rcmed_origin
        )

        self.esgf_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.esgf_origin
        )

        self.dap_ds = Dataset(
            self.lats,
            self.lons,
            self.times,
            self.values,
            variable=self.variable,
            units=self.units,
            name=self.name,
            origin=self.dap_origin
        )

        self.subregions = [
            Bounds(-10, 10, -20, 20),
            Bounds(-5, 5, -15, 15)
        ]

        self.evaluation = Evaluation(
            self.local_ds,
            [self.rcmed_ds, self.esgf_ds, self.dap_ds],
            [metrics.Bias(), metrics.TemporalStdDev()],
            subregions=self.subregions
        )

    @classmethod
    def tearDownClass(self):
        if os.path.isfile('/tmp/test_config.yaml'):
            os.remove('/tmp/test_config.yaml')

    def test_full_export(self):
        file_path = '/tmp/test_config.yaml'
        writer.export_evaluation_to_config(
            self.evaluation,
            file_path=file_path
        )

        self.assertTrue(os.path.isfile(file_path))

    def test_proper_metric_export(self):
        file_path = '/tmp/test_config.yaml'
        writer.export_evaluation_to_config(
            self.evaluation,
            file_path=file_path
        )

        data = yaml.load(open(file_path, 'r'))

        self.assertTrue('metrics' in data)
        self.assertTrue(type(data['metrics']) == type(list()))

        for metric in self.evaluation.metrics:
            self.assertTrue(metric.__class__.__name__ in data['metrics'])

        for metric in self.evaluation.unary_metrics:
            self.assertTrue(metric.__class__.__name__ in data['metrics'])

        total_eval_metrics = (
            len(self.evaluation.metrics) +
            len(self.evaluation.unary_metrics)
        )

        self.assertTrue(total_eval_metrics, len(data['metrics']))

    def test_proper_dataset_export(self):
        file_path = '/tmp/test_config.yaml'
        writer.export_evaluation_to_config(
            self.evaluation,
            file_path=file_path
        )

        data = yaml.load(open(file_path, 'r'))

        self.assertTrue('datasets' in data)
        self.assertTrue('reference' in data['datasets'])
        self.assertTrue('targets' in data['datasets'])

        self.assertAlmostEqual(
            writer.generate_dataset_information(self.evaluation),
            data['datasets']
        )

    def test_proper_evaluation_setting_export(self):
        file_path = '/tmp/test_config.yaml'
        writer.export_evaluation_to_config(
            self.evaluation,
            file_path=file_path
        )

        data = yaml.load(open(file_path, 'r'))

        self.assertTrue('evaluation' in data)
        self.assertTrue('temporal_time_delta' in data['evaluation'])
        self.assertTrue('spatial_regrid_lats' in data['evaluation'])
        self.assertTrue('spatial_regrid_lons' in data['evaluation'])
        self.assertTrue('subset' in data['evaluation'])

        self.assertAlmostEqual(
            writer.generate_evaluation_information(self.evaluation),
            data['evaluation']
        )

    def test_proper_subregion_export(self):
        file_path = '/tmp/test_config.yaml'
        writer.export_evaluation_to_config(
            self.evaluation,
            file_path=file_path
        )

        data = yaml.load(open(file_path, 'r'))

        self.assertTrue('subregions' in data)

        first_bounds = [
            self.subregions[0].lat_min,
            self.subregions[0].lat_max,
            self.subregions[0].lon_min,
            self.subregions[0].lon_max,
        ]
        second_bounds = [
            self.subregions[1].lat_min,
            self.subregions[1].lat_max,
            self.subregions[1].lon_min,
            self.subregions[1].lon_max,
        ]

        self.assertEqual(first_bounds, data['subregions'][0])
        self.assertEqual(second_bounds, data['subregions'][1])
