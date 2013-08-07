#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import unittest
import datetime
from ocw import dataset_processor as dp
from ocw import dataset as ds
import numpy as np
import numpy.ma as ma


class TestTemporalRebin(unittest.TestCase):
    
    def setUp(self):
        self.input_dataset = ten_year_monthly_dataset()
        pass
        
    
    def test__congrid_neighbor(self):
        pass
    


class TestRcmesSpatialRegrid(unittest.TestCase):

    def test_return_array_shape(self):
        spatial_values = np.ones([90,180])
        spatial_values = ma.array(spatial_values)
        
        lat_range = ma.array(range(-89, 90, 2))
        lon_range = ma.array(range(-179, 180, 2))
        
        lons, lats = np.meshgrid(lon_range, lat_range)
        # Convert these to masked arrays
        lats = ma.array(lats)
        lons = ma.array(lons)
        
        lat2_range = np.array(range(-89, 90, 4))
        lon2_range = np.array(range(-179, 180, 4))
        
        lons2, lats2 = np.meshgrid(lon2_range, lat2_range)
        # Convert to masked arrays
        lats2 = ma.array(lats2)
        lons2 = ma.array(lons2)

        regridded_values = dp._rcmes_spatial_regrid(spatial_values, lats, lons, lats2, lons2)
        self.assertEqual(regridded_values.shape, lats2.shape)
        self.assertEqual(regridded_values.shape, lons2.shape)

class TestSpatialRegrid(unittest.TestCase):
    
    def setUp(self):
        self.input_dataset = ten_year_monthly_dataset()
        self.new_lats = np.array(range(-89, 90, 4))
        self.new_lons = np.array(range(-179, 180, 4))
        self.regridded_dataset = dp.spatial_regrid(self.input_dataset, self.new_lats, self.new_lons)
    # Custom Assertions to handle Numpy Arrays
    def assert1DArraysEqual(self, array1, array2):
        self.assertSequenceEqual(tuple(array1), tuple(array2))

    def test_returned_lats(self):
        self.assert1DArraysEqual(self.regridded_dataset.lats, self.new_lats)

    def test_returned_lons(self):
        self.assert1DArraysEqual(self.regridded_dataset.lons, self.new_lons)

    def test_shape_of_values(self):
        regridded_data_shape = self.regridded_dataset.values.shape
        expected_data_shape = (len(self.input_dataset.times), len(self.new_lats), len(self.new_lons))
        self.assertSequenceEqual(regridded_data_shape, expected_data_shape)

def ten_year_monthly_dataset():
        lats = np.array(range(-89, 90, 2))
        lons = np.array(range(-179, 180, 2))
        # Ten Years of monthly data
        times = np.array([datetime.datetime(year, month, 1) for year in range(2000, 2010) for month in range(1, 13)])
        values = np.ones([len(times), len(lats), len(lons)])
        input_dataset = ds.Dataset(lats, lons, times, values, variable="test variable name")
        return input_dataset



if __name__ == '__main__':
    unittest.main()