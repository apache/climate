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

'''Unit test for the metrics.py module.'''

import unittest
import datetime as dt

from ocw.dataset import Dataset
import ocw.metrics as metrics

import numpy as np
import numpy.ma as ma
import numpy.testing as npt


class TestBias(unittest.TestCase):
    '''Test the metrics.Bias metric.'''

    def setUp(self):
        self.bias = metrics.Bias()
        # Initialize reference dataset
        self.reference_lat = np.array([10, 12, 14, 16, 18])
        self.reference_lon = np.array([100, 102, 104, 106, 108])
        self.reference_time = np.array(
            [dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.reference_value = flat_array.reshape(12, 5, 5)
        self.reference_variable = 'prec'
        self.reference_dataset = Dataset(self.reference_lat,
                                         self.reference_lon,
                                         self.reference_time,
                                         self.reference_value,
                                         self.reference_variable)
        # Initialize target dataset
        self.target_lat = np.array([1, 2, 4, 6, 8])
        self.target_lon = np.array([10, 12, 14, 16, 18])
        self.target_time = np.array(
            [dt.datetime(2001, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300, 600))
        self.target_value = flat_array.reshape(12, 5, 5)
        self.target_variable = 'tasmax'
        self.target_dataset = Dataset(self.target_lat,
                                      self.target_lon,
                                      self.target_time,
                                      self.target_value,
                                      self.target_variable)

    def test_function_run(self):
        '''Test bias function between reference dataset and target dataset.'''
        expected_result = np.zeros((12, 5, 5), dtype=np.int)
        expected_result.fill(-300)
        np.testing.assert_array_equal(self.bias.run(
            self.target_dataset, self.reference_dataset), expected_result)


class TestSpatialPatternTaylorDiagram(unittest.TestCase):
    '''Test the metrics.SpatialPatternTaylorDiagram'''

    def setUp(self):
        self.taylor_diagram = metrics.SpatialPatternTaylorDiagram()
        self.ref_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 5
            np.arange(0, 1500, 5).reshape(12, 5, 5),
            'ds1'
        )

        self.tar_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 2
            np.arange(0, 600, 2).reshape(12, 5, 5),
            'ds2'
        )

    def test_function_run(self):
        np.testing.assert_array_equal(self.taylor_diagram.run(
            self.ref_dataset, self.tar_dataset), ma.array([0.4, 1.0]))


class TestTemporalStdDev(unittest.TestCase):
    '''Test the metrics.TemporalStdDev metric.'''

    def setUp(self):
        self.temporal_std_dev = metrics.TemporalStdDev()
        # Initialize target dataset
        self.target_lat = np.array([10, 12, 14, 16, 18])
        self.target_lon = np.array([100, 102, 104, 106, 108])
        self.target_time = np.array(
            [dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.target_value = flat_array.reshape(12, 5, 5)
        self.target_variable = 'prec'
        self.target_dataset = Dataset(self.target_lat,
                                      self.target_lon,
                                      self.target_time,
                                      self.target_value,
                                      self.target_variable)

    def test_function_run(self):
        '''Test TemporalStdDev function for target dataset.'''
        expected_result = np.zeros((5, 5),)
        expected_result.fill(90.13878189)
        npt.assert_almost_equal(self.temporal_std_dev.run(
            self.target_dataset), expected_result)


class TestStdDevRatio(unittest.TestCase):
    '''Test the metrics.StdDevRatio metric'''

    def setUp(self):
        self.std_dev_ratio = metrics.StdDevRatio()
        self.ref_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 5
            np.arange(0, 1500, 5).reshape(12, 5, 5),
            'ds1'
        )

        self.tar_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 2
            np.arange(0, 600, 2).reshape(12, 5, 5),
            'ds2'
        )

    def test_function_run(self):
        self.assertTrue(self.std_dev_ratio.run(
            self.ref_dataset, self.tar_dataset), 0.4)


class TestPatternCorrelation(unittest.TestCase):
    '''Test the metrics.PatternCorrelation metric'''

    def setUp(self):
        self.pattern_correlation = metrics.PatternCorrelation()
        self.ref_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 5
            np.arange(0, 1500, 5).reshape(12, 5, 5),
            'ds1'
        )

        self.tar_dataset = Dataset(
            np.array([1., 1., 1., 1., 1.]),
            np.array([1., 1., 1., 1., 1.]),
            np.array([dt.datetime(2000, x, 1) for x in range(1, 13)]),
            # Reshapped array with 300 values incremented by 2
            np.arange(0, 600, 2).reshape(12, 5, 5),
            'ds2'
        )

    def test_function_run(self):
        pattern = self.pattern_correlation.run(
            self.tar_dataset, self.ref_dataset)
        self.assertEqual(pattern, 1.0)


class TestTemporalCorrelation(unittest.TestCase):
    '''Test the metrics.TemporalCorrelation metric.'''

    def setUp(self):
        # Set metric.
        self.metric = metrics.TemporalCorrelation()
        # Initialize reference dataset.
        self.ref_lats = np.array([10, 20, 30, 40, 50])
        self.ref_lons = np.array([5, 15, 25, 35, 45])
        self.ref_times = np.array([dt.datetime(2000, x, 1)
                                   for x in range(1, 13)])
        self.ref_values = np.array(range(300)).reshape(12, 5, 5)
        self.ref_variable = "ref"
        self.ref_dataset = Dataset(self.ref_lats,
                                   self.ref_lons,
                                   self.ref_times,
                                   self.ref_values,
                                   self.ref_variable)
        # Initialize target datasets.
        self.tgt_lats = np.array([10, 20, 30, 40, 50])
        self.tgt_lons = np.array([5, 15, 25, 35, 45])
        self.tgt_times = np.array([dt.datetime(2000, x, 1)
                                   for x in range(1, 13)])
        self.tgt_variable = "tgt"
        self.tgt_values_inc = np.array(range(300, 600)).reshape(12, 5, 5)
        self.tgt_values_dec = np.array(range(299, -1, -1)).reshape(12, 5, 5)
        self.tgt_dataset_inc = Dataset(self.tgt_lats,
                                       self.tgt_lons,
                                       self.tgt_times,
                                       self.tgt_values_inc,
                                       self.tgt_variable)
        self.tgt_dataset_dec = Dataset(self.tgt_lats,
                                       self.tgt_lons,
                                       self.tgt_times,
                                       self.tgt_values_dec,
                                       self.tgt_variable)

    def test_identical_inputs(self):
        expected = np.ones(25).reshape(5, 5)
        tc = self.metric.run(self.ref_dataset, self.ref_dataset)
        np.testing.assert_array_equal(tc, expected)

    def test_positive_correlation(self):
        expected = np.ones(25).reshape(5, 5)
        tc = self.metric.run(self.ref_dataset, self.tgt_dataset_inc)
        np.testing.assert_array_equal(tc, expected)

    def test_negative_correlation(self):
        expected_tc = np.array([-1] * 25).reshape(5, 5)
        tc = self.metric.run(self.ref_dataset, self.tgt_dataset_dec)
        np.testing.assert_array_equal(tc, expected_tc)


class TestTemporalMeanBias(unittest.TestCase):
    '''Test the metrics.TemporalMeanBias metric.'''

    def setUp(self):
        self.mean_bias = metrics.TemporalMeanBias()
        # Initialize reference dataset
        self.reference_lat = np.array([10, 12, 14, 16, 18])
        self.reference_lon = np.array([100, 102, 104, 106, 108])
        self.reference_time = np.array(
            [dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.reference_value = flat_array.reshape(12, 5, 5)
        self.reference_variable = 'prec'
        self.reference_dataset = Dataset(self.reference_lat,
                                         self.reference_lon,
                                         self.reference_time,
                                         self.reference_value,
                                         self.reference_variable)
        # Initialize target dataset
        self.target_lat = np.array([1, 2, 4, 6, 8])
        self.target_lon = np.array([10, 12, 14, 16, 18])
        self.target_time = np.array(
            [dt.datetime(2001, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300, 600))
        self.target_value = flat_array.reshape(12, 5, 5)
        self.target_variable = 'tasmax'
        self.target_dataset = Dataset(self.target_lat,
                                      self.target_lon,
                                      self.target_time,
                                      self.target_value,
                                      self.target_variable)

    def test_function_run(self):
        '''
        Test mean bias function between reference dataset and target dataset.
        '''
        expected_result = np.zeros((5, 5), dtype=np.int)
        expected_result.fill(-300)
        np.testing.assert_array_equal(self.mean_bias.run(
            self.target_dataset, self.reference_dataset), expected_result)


class TestRMSError(unittest.TestCase):
    '''Test the metrics.RMSError metric.'''

    def setUp(self):
        # Set metric.
        self.metric = metrics.RMSError()
        # Initialize reference dataset.
        self.ref_lats = np.array([10, 20, 30, 40, 50])
        self.ref_lons = np.array([5, 15, 25, 35, 45])
        self.ref_times = np.array([dt.datetime(2000, x, 1)
                                   for x in range(1, 13)])
        self.ref_values = np.array([4] * 300).reshape(12, 5, 5)
        self.ref_variable = "ref"
        self.ref_dataset = Dataset(self.ref_lats,
                                   self.ref_lons,
                                   self.ref_times,
                                   self.ref_values,
                                   self.ref_variable)
        # Initialize target dataset.
        self.tgt_lats = np.array([10, 20, 30, 40, 50])
        self.tgt_lons = np.array([5, 15, 25, 35, 45])
        self.tgt_times = np.array([dt.datetime(2000, x, 1)
                                   for x in range(1, 13)])
        self.tgt_values = np.array([2] * 300).reshape(12, 5, 5)
        self.tgt_variable = "tgt"
        self.tgt_dataset = Dataset(self.tgt_lats,
                                   self.tgt_lons,
                                   self.tgt_times,
                                   self.tgt_values,
                                   self.tgt_variable)

    def test_function_run(self):
        result = self.metric.run(self.ref_dataset, self.tgt_dataset)
        self.assertEqual(result, 2.0)


if __name__ == '__main__':
    unittest.main()
