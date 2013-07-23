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

'''Unit tests for the Evaluation.py module'''

import unittest
import numpy as np
import datetime as dt
from dataset import Dataset
from evaluation import Evaluation

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.eval = Evaluation()

    def test_init(self):
        self.assertEquals(self.eval.ref_dataset, None)
        self.assertEquals(self.eval.target_datasets, [])
        self.assertEquals(self.eval.metrics, [])

    def test_add_ref_dataset(self):
        # Create an example dataset to add
        lat = np.array([10, 12, 14, 16, 18])
        lon = np.array([100, 102, 104, 106, 108])
        time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        value = flat_array.reshape(12, 5, 5)
        variable = 'prec'
        test_dataset = Dataset(lat, lon, time, value, variable)

        self.eval.add_ref_dataset(test_dataset)

        self.assertEqual(self.eval.ref_dataset.variable, 'prec')

    def test_add_dataset(self):
        lat = np.array([10, 12, 14, 16, 18])
        lon = np.array([100, 102, 104, 106, 108])
        time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        value = flat_array.reshape(12, 5, 5)
        variable = 'prec'
        test_dataset = Dataset(lat, lon, time, value, variable)

        self.eval.add_dataset(test_dataset)

        self.assertEqual(self.eval.target_datasets[0].variable, 'prec')

    def test_add_datasets(self):
        lat = np.array([10, 12, 14, 16, 18])
        lon = np.array([100, 102, 104, 106, 108])
        time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        value = flat_array.reshape(12, 5, 5)
        variable = 'prec'
        other_var = 'temp'
        test_dataset = Dataset(lat, lon, time, value, variable)
        another_test_dataset = Dataset(lat, lon, time, value, other_var)

        self.eval.add_datasets([test_dataset, another_test_dataset])

        self.assertEqual(len(self.eval.target_datasets), 2)
        self.assertEqual(self.eval.target_datasets[0].variable, variable)
        self.assertEqual(self.eval.target_datasets[1].variable, other_var)

    def test_add_metric(self):
        test_func = lambda x: x + 1
        self.eval.add_metric(test_func)

        self.assertEqual(self.eval.metrics[0](2), 3)


if __name__  == '__main__':
    unittest.main()
