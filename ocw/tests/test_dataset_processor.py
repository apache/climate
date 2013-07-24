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
from ocw import dataset_processor as dp
import numpy as np
import numpy.ma as ma


class TestTemporalRebin(unittest.TestCase):
    
    def setUp(self):
        pass
        
    
    def test__congrid_neighbor(self):
        pass
    


class TestRcmesSpatialRegrid(unittest.TestCase):

    def test_return_array_shape(self):
        spatial_values = np.ones([90,180])
        spatial_values = ma.array(spatial_values)
        
        lat_range = ma.array(range(-89, 90, 2))
        lon_range = ma.array(range(-179, 180, 2))
        
        lats, lons = np.meshgrid(lat_range, lon_range)
        # Convert these to masked arrays
        lats = ma.array(lats)
        lons = ma.array(lons)
        
        lat2_range = np.array(range(-89, 90, 4))
        lon2_range = np.array(range(-179, 180, 4))
        
        lats2, lons2 = np.meshgrid(lat2_range, lon2_range)
        # Convert to masked arrays
        lats2 = ma.array(lats2)
        lons2 = ma.array(lons2)

        regridded_values = dp._rcmes_spatial_regrid(spatial_values, lats, lons, lats2, lons2)
        self.assertEqual(regridded_values.shape, lats2.shape)


if __name__ == '__main__':
    unittest.main()