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

'''Unit tests for the Dataset.py module'''

import unittest
from ocw.dataset import Dataset, Bounds
import numpy as np
import datetime as dt


class TestDatasetAttributes(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.name = 'foo'
        self.origin = {'path': '/a/fake/file/path'}
        self.test_dataset = Dataset(self.lat,
                                    self.lon,
                                    self.time,
                                    self.value,
                                    variable=self.variable,
                                    name=self.name,
                                    origin=self.origin)

    def test_lats(self):
        self.assertItemsEqual(self.test_dataset.lats, self.lat)

    def test_lons(self):
        self.assertItemsEqual(self.test_dataset.lons, self.lon)

    def test_times(self):
        self.assertItemsEqual(self.test_dataset.times, self.time)

    def test_values(self):
        self.assertEqual(self.test_dataset.values.all(), self.value.all())

    def test_variable(self):
        self.assertEqual(self.test_dataset.variable, self.variable)

    def test_name(self):
        self.assertEqual(self.test_dataset.name, self.name)

    def test_origin(self):
        self.assertEqual(self.test_dataset.origin, self.origin)


class TestInvalidDatasetInit(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.values_in_wrong_order = flat_array.reshape(5, 5, 12)

    def test_bad_lat_shape(self):
        self.lat = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_lon_shape(self):
        self.lon = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_times_shape(self):
        self.time = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_values_shape(self):
        self.value = np.array([1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')
        self.value = self.value.reshape(1, 5)
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_values_shape_mismatch(self):
        # If we change lats to this the shape of value will not match
        # up with the length of the lats array.
        self.lat = self.lat[:-2]
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_values_given_in_wrong_order(self):
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.values_in_wrong_order)

    def test_lons_values_incorrectly_gridded(self):
        times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        lats = np.arange(-30, 30)
        bad_lons = np.arange(360)
        flat_array = np.arange(len(times) * len(lats) * len(bad_lons))
        values = flat_array.reshape(len(times), len(lats), len(bad_lons))

        ds = Dataset(lats, bad_lons, times, values)
        np.testing.assert_array_equal(ds.lons, np.arange(-180, 180))

    def test_reversed_lats(self):
        ds = Dataset(self.lat[::-1], self.lon, self.time, self.value)
        np.testing.assert_array_equal(ds.lats, self.lat)


class TestDatasetFunctions(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)

    def test_spatial_boundaries(self):
        self.assertEqual(
            self.test_dataset.spatial_boundaries(),
            (min(self.lat), max(self.lat), min(self.lon), max(self.lon)))

    def test_time_range(self):
        self.assertEqual(
            self.test_dataset.time_range(),
            (dt.datetime(2000, 1, 1), dt.datetime(2000, 12, 1)))

    def test_spatial_resolution(self):
        self.assertEqual(self.test_dataset.spatial_resolution(), (2, 2))

    def test_spatial_resolution_2_dim_lat_lon(self):
        self.lat = np.array([10, 12, 14, 16, 18, 20])
        self.lon = np.array([100, 102, 104, 106, 108, 110])
        self.lat = self.lat.reshape(3, 2)
        self.lon = self.lon.reshape(3, 2)
        flat_array = np.array(range(72))
        self.value = flat_array.reshape(12, 3, 2)
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)
        self.assertEqual(self.test_dataset.spatial_resolution(), (6, 6))

    def test_temporal_resolution_hourly(self):
        self.time = np.array([dt.datetime(2000, 1, 1),
                              dt.datetime(2000, 1, 1)])
        flat_array = np.array(range(50))
        self.value = flat_array.reshape(2, 5, 5)
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)
        self.assertEqual(self.test_dataset.temporal_resolution(), 'minutely')

    def test_temporal_resolution_monthly(self):
        self.assertEqual(self.test_dataset.temporal_resolution(), 'monthly')

    def test_temporal_resolution_daily(self):
        self.time = np.array([dt.datetime(2000, 3, x) for x in range(1, 31)])
        flat_array = np.array(range(750))
        self.value = flat_array.reshape(30, 5, 5)
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)
        self.assertEqual(self.test_dataset.temporal_resolution(), 'daily')

    def test_temporal_resolution_yearly(self):
        self.time = np.array([dt.datetime(x, 6, 1) for x in range(2000, 2015)])
        flat_array = np.array(range(375))
        self.value = flat_array.reshape(15, 5, 5)
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)
        self.assertEqual(self.test_dataset.temporal_resolution(), 'yearly')

    def test_str_(self):
        dataset = self.test_dataset
        lat_min, lat_max, lon_min, lon_max = dataset.spatial_boundaries()
        start, end = dataset.time_range()
        lat_range = "({}, {})".format(lat_min, lon_min)
        lon_range = "({}, {})".format(lon_min, lon_min)
        time_range = "({}, {})".format(start, end)

        formatted_repr = (
            "<Dataset - name: {}, "
            "lat-range: {}, "
            "lon-range: {}, "
            "time_range: {}, "
            "var: {}, "
            "units: {}>"
        )

        output = formatted_repr.format(
            dataset.name if dataset.name != "" else None,
            lat_range,
            lon_range,
            time_range,
            dataset.variable,
            dataset.units
        )
        self.assertEqual(str(self.test_dataset), output)


class TestBounds(unittest.TestCase):
    def setUp(self):
        self.bounds = Bounds(-80, 80,                # Lats
                             -160, 160,               # Lons
                             dt.datetime(2000, 1, 1),  # Start time
                             dt.datetime(2002, 1, 1))  # End time
        self.another_bounds = Bounds(-80, 80,                # Lats
                                     -160, 160)

    def test_setter_methods(self):
        self.bounds.lat_min = -10
        self.bounds.lat_max = 10
        self.bounds.lon_min = -120
        self.bounds.lon_max = 120
        self.bounds.start = dt.datetime(2000, 1, 2)
        self.bounds.end = dt.datetime(2002, 1, 4)

        self.assertEqual(self.bounds.lat_min, -10)
        self.assertEqual(self.bounds.lat_max, 10)
        self.assertEqual(self.bounds.lon_min, -120)
        self.assertEqual(self.bounds.lon_max, 120)
        self.assertEqual(self.bounds.start, dt.datetime(2000, 1, 2))
        self.assertEqual(self.bounds.end, dt.datetime(2002, 1, 4))

    # Latitude tests
    def test_inverted_min_max_lat(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_min = 81

        with self.assertRaises(ValueError):
            self.bounds.lat_max = -81

    # Lat Min
    def test_out_of_bounds_lat_min(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_min = -91

        with self.assertRaises(ValueError):
            self.bounds.lat_min = 91

    # Lat Max
    def test_out_of_bounds_lat_max(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_max = -91

        with self.assertRaises(ValueError):
            self.bounds.lat_max = 91

    # Longitude tests
    def test_inverted_max_max_lon(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_min = 161

        with self.assertRaises(ValueError):
            self.bounds.lon_max = -161

    # Lon Min
    def test_out_of_bounds_lon_min(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_min = -181

        with self.assertRaises(ValueError):
            self.bounds.lon_min = 181

    # Lon Max
    def test_out_of_bounds_lon_max(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_max = -181

        with self.assertRaises(ValueError):
            self.bounds.lon_max = 181

    # Temporal tests
    def test_inverted_start_end_times(self):
        with self.assertRaises(ValueError):
            self.bounds.start = dt.datetime(2003, 1, 1)

        with self.assertRaises(ValueError):
            self.bounds.end = dt.datetime(1999, 1, 1)

    # Start tests
    def test_invalid_start(self):
        with self.assertRaises(ValueError):
            self.bounds.start = "This is not a date time object"

    # End tests
    def test_invalid_end(self):
        with self.assertRaises(ValueError):
            self.bounds.end = "This is not a date time object"

    # Start tests
    def test_none_value_start(self):
        self.assertEqual(self.another_bounds.start, None)

    # End tests
    def test_none_value_end(self):
        self.assertEqual(self.another_bounds.end, None)

    def test__str__(self):
        lat_range = "({}, {})".format(self.bounds.lat_min, self.bounds.lat_max)
        lon_range = "({}, {})".format(self.bounds.lon_min, self.bounds.lon_max)
        time_range = "({}, {})".format(self.bounds.start, self.bounds.end)

        formatted_repr = (
            "<Bounds - "
            "lat-range: {}, "
            "lon-range: {}, "
            "time_range: {}> "
        )

        output = formatted_repr.format(
            lat_range,
            lon_range,
            time_range,
        )
        self.assertEqual(str(self.bounds), output)

if __name__ == '__main__':
    unittest.main()
