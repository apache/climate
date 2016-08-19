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


import ocw.data_source.podaac as podaac
import unittest
import os
from ocw.dataset import Dataset


class TestPodaacDataSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.datasetId = 'PODAAC-GHCMC-4FM02'
        cls.datasetShortName = 'CMC0.2deg-CMC-L4-GLOB-v2.0'
        cls.variable = 'sea_ice_fraction'
        cls.name = 'PO.DAAC_test_dataset'
        cls.file_path = os.path.dirname(os.path.abspath(__file__))
        cls.format = '.nc'
        cls.dataset = podaac.load_dataset(
            cls.variable, cls.datasetId, cls.datasetShortName, cls.name)

    def test_is_dataset(self):
        self.assertTrue(isinstance(self.dataset, Dataset))

    def test_dataset_lats(self):
        self.assertEquals(len(self.dataset.lats), 901)

    def test_dataset_lons(self):
        self.assertEquals(len(self.dataset.lons), 1800)

    def test_dataset_times(self):
        self.assertEquals(len(self.dataset.times), 1)

    def test_dataset_values(self):
        self.assertEquals(len(self.dataset.values), 1)

    def test_valid_date_conversion(self):
        start = dt.datetime(2006, 6, 7, 12)
        self.assertTrue(start == self.dataset.times[0])

    def test_dataset_origin(self):
        self.assertEquals(self.dataset.origin['source'], 'PO.DAAC')
        self.assertEquals(self.dataset.origin['url'], 'podaac.jpl.nasa.gov/ws')

    def test_custom_name(self):
        self.assertEquals(self.dataset.name, self.name)


if __name__ == '__main__':
    unittest.main()
