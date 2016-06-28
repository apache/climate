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

import unittest
import datetime as dt
import ocw.data_source.dap as dap
from ocw.dataset import Dataset


class TestDap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.url = 'http://test.opendap.org/opendap/data/ncml/agg/dated/'\
                  'CG2006158_120000h_usfc.nc'
        cls.name = 'foo'
        cls.dataset = dap.load(cls.url, 'CGusfc', name=cls.name)

    def test_dataset_is_returned(self):
        self.assertTrue(isinstance(self.dataset, Dataset))

    def test_correct_lat_shape(self):
        self.assertEquals(len(self.dataset.lats), 29)

    def test_correct_lon_shape(self):
        self.assertEquals(len(self.dataset.lons), 26)

    def test_correct_time_shape(self):
        self.assertEquals(len(self.dataset.times), 1)

    def test_valid_date_conversion(self):
        start = dt.datetime(2006, 6, 7, 12)
        self.assertTrue(start == self.dataset.times[0])

    def test_custom_dataset_name(self):
        self.assertEquals(self.dataset.name, self.name)

    def test_dataset_origin(self):
        self.assertEquals(self.dataset.origin['source'], 'dap')
        self.assertEquals(self.dataset.origin['url'], self.url)

if __name__ == '__main__':
    unittest.main()
