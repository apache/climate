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

from ocw.dataset import Dataset
from ocw.evaluation import Evaluation
import ocw.metrics as metrics
import configuration_writer as writer

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

        self.exported_info = writer.generate_dataset_information(self.dataset)

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

        self.exported_info = writer.generate_dataset_information(self.dataset)

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

        self.exported_info = writer.generate_dataset_information(self.dataset)

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

        self.exported_info = writer.generate_dataset_information(self.dataset)

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
