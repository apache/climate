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
"""Tests for local.py, an OCW (netCDF, HDF5) file loading library."""

# Needed Python 2/3 urllib compatibility
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

import datetime
import unittest
import os
import netCDF4
import numpy as np

import ocw.data_source.local as local


class TestLoadFile(unittest.TestCase):
    """Tests for load_file method."""

    @classmethod
    def setUpClass(cls):
        """Prepare a netCDF file once to use for all tests."""
        cls.file_path = create_netcdf_file()

    @classmethod
    def tearDownClass(cls):
        """Remove the no longer needed testing file at the end of the tests."""
        os.remove(cls.file_path)

    def setUp(self):
        """Open and read in attributes of netCDF test file."""
        self.netcdf_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netcdf_file.variables['latitude'][:]
        self.longitudes = self.netcdf_file.variables['longitude'][:]
        self.alt_lats = self.netcdf_file.variables['alt_lat'][:]
        self.alt_lons = self.netcdf_file.variables['alt_lon'][:]
        self.values = self.netcdf_file.variables['value'][:]
        self.variable_name_list = ['latitude', 'longitude', 'time', 'level',
                                   'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']

    def tearDown(self):
        """Close file object so that it may be re-read in the next test."""
        self.netcdf_file.close()

    def test_load_invalid_file_path(self):
        """To test load_file an invalid path raises an exception."""
        self.invalid_netcdf_path = '/invalid/path'
        with self.assertRaises(ValueError):
            local.load_file(file_path=self.invalid_netcdf_path,
                            variable_name='test variable')

    def test_function_load_file_lats(self):
        """Test load_file function for latitudes."""
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value").lats, self.latitudes)

    def test_function_load_file_lons(self):
        """Test load_file function for longitudes."""
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value").lons, self.longitudes)

    def test_function_load_file_times(self):
        """Test load_file function for times."""
        new_times = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value").times, new_times)

    def test_function_load_file_alt_lats(self):
        """Test load_file function for lats with different variable names."""
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value", lat_name="alt_lat").lats, self.alt_lats)

    def test_function_load_file_alt_lons(self):
        """Test load_file function for lons with different variable names."""
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value", lon_name="alt_lon").lons, self.alt_lons)

    def test_function_load_file_alt_times(self):
        """Test load_file function for times with different variable names."""
        new_times = datetime.datetime(2001, 4, 1), datetime.datetime(
            2001, 5, 1), datetime.datetime(2001, 6, 1)
        np.testing.assert_array_equal(local.load_file(
            self.file_path, "value", time_name="alt_time").times, new_times)

    def test_function_load_file_values(self):
        """Test load_file function for values."""
        new_values = self.values[:, 0, :, :]
        self.assertTrue(np.allclose(local.load_file(
            self.file_path, "value").values, new_values))

    def test_custom_dataset_name(self):
        """Test adding a custom name to a dataset."""
        dataset = local.load_file(self.file_path, 'value', name='foo')
        self.assertEqual(dataset.name, 'foo')

    def test_dataset_origin(self):
        """Test that dataset origin is local."""
        dataset = local.load_file(self.file_path, 'value', elevation_index=1)
        expected_keys = {'source', 'path', 'lat_name', 'lon_name', 'time_name',
                         'elevation_index'}
        self.assertEqual(set(dataset.origin.keys()), expected_keys)
        self.assertEqual(dataset.origin['source'], 'local')


class TestLoadMultipleFiles(unittest.TestCase):
    """Tests for the load_multiple_files method."""

    @classmethod
    def setUpClass(cls):
        """Prepare a netCDF file once to use for all tests."""
        cls.file_path = create_netcdf_file()

    @classmethod
    def tearDownClass(cls):
        """Remove the no longer needed testing file at the end of the tests."""
        os.remove(cls.file_path)

    def setUp(self):
        """Open and read in attributes of netCDF test file."""
        self.netcdf_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netcdf_file.variables['latitude'][:]
        self.longitudes = self.netcdf_file.variables['longitude'][:]
        self.values = self.netcdf_file.variables['value'][:]
        self.variable_name_list = ['latitude',
                                   'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']

    def tearDown(self):
        """Close file object so that it may be re-read in the next test."""
        self.netcdf_file.close()

    def test_function_load_multiple_files_data_name(self):
        """Test load_multiple_file function for dataset name."""
        dataset = local.load_multiple_files(self.file_path, "value")
        self.assertEqual([dataset[0].name], [''])

    def test_function_load_multiple_files_lons(self):
        """Test load_multiple_file function for longitudes."""
        dataset = local.load_multiple_files(self.file_path, "value")
        np.testing.assert_array_equal(dataset[0].lons, self.longitudes)

    def test_function_load_multiple_files_times(self):
        """Test load_multiple_files function for times."""
        dataset = local.load_multiple_files(self.file_path, "value")

        new_times = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        np.testing.assert_array_equal(dataset[0].times, new_times)

    def test_function_load_multiple_files_values(self):
        """Test load_multiple_files function for values."""
        new_values = self.values[:, 0, :, :]
        dataset = local.load_multiple_files(
            self.file_path, "value")
        self.assertTrue(np.allclose(dataset[0].values, new_values))

    def test_load_multiple_files_custom_dataset_name(self):
        """Test adding a custom name to a dataset."""
        dataset = local.load_multiple_files(self.file_path,
                                            "value",
                                            generic_dataset_name=True,
                                            dataset_name=['foo'])
        self.assertEqual(dataset[0].name, 'foo')

    def test_dataset_origin(self):
        """Test that dataset origin is local."""
        dataset = local.load_multiple_files(self.file_path, 'value')
        expected_keys = {'source', 'path', 'lat_name', 'lon_name', 'time_name'}
        self.assertEqual(set(dataset[0].origin.keys()), expected_keys)
        self.assertEqual(dataset[0].origin['source'], 'local')


class TestLoadDatasetFromMultipleNetcdfFiles(unittest.TestCase):
    """Tests for load_dataset_from_multiple_netcdf_files method."""

    @classmethod
    def setUpClass(cls):
        """Create, read in, and record attributes of a netCDF file for tests."""
        cls.file_path = create_netcdf_file()
        cls.netcdf_file = netCDF4.Dataset(cls.file_path, 'r')
        cls.latitudes = cls.netcdf_file.variables['latitude'][:]
        cls.longitudes = cls.netcdf_file.variables['longitude'][:]
        cls.alt_lats = cls.netcdf_file.variables['alt_lat'][:]
        cls.alt_lons = cls.netcdf_file.variables['alt_lon'][:]
        cls.values = cls.netcdf_file.variables['value'][:]
        cls.variable_name_list = ['latitude', 'longitude', 'time', 'level',
                                  'value']
        cls.possible_value_name = ['latitude', 'longitude', 'time', 'level']
        cls.dataset = local.load_dataset_from_multiple_netcdf_files(
            variable_name='value',
            file_path='',
            filename_pattern=[cls.file_path])
        cls.alt_dataset = local.load_dataset_from_multiple_netcdf_files(
            variable_name='value',
            lat_name='alt_lat',
            lon_name='alt_lon',
            time_name='alt_time',
            file_path='',
            filename_pattern=[cls.file_path])

    @classmethod
    def tearDownClass(cls):
        """Remove the no longer needed testing file at the end of the tests."""
        cls.netcdf_file.close()
        os.remove(cls.file_path)

    def test_variable_name(self):
        """Test that dataset contains a variable value."""
        self.assertEqual(self.dataset.variable, 'value')

    def test_function_load_dataset_from_multiple_netcdf_files_lats(self):
        """Test load_multiple_files function for times."""
        np.testing.assert_array_equal(self.dataset.lats, self.latitudes)

    def test_function_load_dataset_from_multiple_netcdf_files_lons(self):
        """Test load_multiple_files function for times."""
        np.testing.assert_array_equal(self.dataset.lons, self.longitudes)

    def test_function_load_dataset_from_multiple_netcdf_files_times(self):
        """Test load_multiple_files function for times."""
        new_times = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        np.testing.assert_array_equal(self.dataset.times, new_times)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_lats(self):
        """Test load_multiple_files function for non-default lats."""
        np.testing.assert_array_equal(self.alt_dataset.lats, self.alt_lats)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_lons(self):
        """Test load_multiple_files function for non-default lons."""
        np.testing.assert_array_equal(self.alt_dataset.lons, self.alt_lons)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_times(self):
        """Test load_multiple_files function for non-default times."""
        new_times = datetime.datetime(2001, 4, 1), datetime.datetime(
            2001, 5, 1), datetime.datetime(2001, 6, 1)
        np.testing.assert_array_equal(self.alt_dataset.times, new_times)

    def test_function_load_dataset_from_multiple_netcdf_files_values(self):
        """Test load_multiple_files function for values."""
        new_values = self.values[:, 0, :, :]
        self.assertTrue(np.allclose(self.dataset.values, new_values))


class TestGetNetcdfVariableNames(unittest.TestCase):
    """Tests for _get_netcdf_variable_name method retrieving variables.

    TestGetNetcdfVariableNames.nc" is a subset of data from
        https://zipper.jpl.nasa.gov/dist/AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc
        Test data obtained with:
        ncea -d time,0,0 AFRICA_KNMI-[...]_tasmax.nc \
         TestGetNetcdfVariableNames.nc
    """

    @classmethod
    def setUpClass(cls):
        """Create a netCDF file with invalid dimensions for tests."""
        cls.test_model = "TestGetNetcdfVariableNames.nc"
        cls.invalid_netcdf_path = create_invalid_dimensions_netcdf_file()

    def setUp(self):
        """Open a valid netCDF file for use in the test."""
        self.netcdf = netCDF4.Dataset(self.test_model, mode='r')

    def tearDown(self):
        """Close file object so that it may be re-read in the next test."""
        self.netcdf.close()

    def test_valid_latitude(self):
        """Test that a latitude variable (rlat) can be found in netCDF file."""
        self.lat = local._get_netcdf_variable_name(local.LAT_NAMES,
                                                   self.netcdf,
                                                   "tasmax")
        self.assertEquals(self.lat, "rlat")

    def test_invalid_dimension_latitude(self):
        """Test than an invalid  latitude variable can be found in file."""
        self.netcdf = netCDF4.Dataset(self.invalid_netcdf_path, mode='r')
        self.lat = local._get_netcdf_variable_name(local.LAT_NAMES,
                                                   self.netcdf,
                                                   "value")
        self.assertEquals(self.lat, "latitude")

    def test_dimension_variable_name_mismatch(self):
        """Test that mismatched latitude variables are found as latitude."""
        self.netcdf = netCDF4.Dataset(self.invalid_netcdf_path, mode='r')
        self.lat = local._get_netcdf_variable_name(
            ["lat_dim"] + local.LAT_NAMES,
            self.netcdf,
            "value")
        self.assertEquals(self.lat, "latitude")

    def test_no_match_latitude(self):
        """Test that retrieving a nonexistent variable name raises exception."""
        with self.assertRaises(ValueError):
            self.lat = local._get_netcdf_variable_name(['notAVarName'],
                                                       self.netcdf,
                                                       "tasmax")


def create_netcdf_file():
    """Create a temporary netCDF file with data used for testing."""
    # To create the temporary netCDF file
    file_path = '/tmp/temporaryNetcdf.nc'
    netcdf_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
    # To create dimensions
    netcdf_file.createDimension('lat_dim', 5)
    netcdf_file.createDimension('lon_dim', 5)
    netcdf_file.createDimension('time_dim', 3)
    netcdf_file.createDimension('level_dim', 2)
    # To create variables
    latitudes = netcdf_file.createVariable('latitude', 'd', ('lat_dim',))
    longitudes = netcdf_file.createVariable('longitude', 'd', ('lon_dim',))
    times = netcdf_file.createVariable('time', 'd', ('time_dim',))
    # unusual variable names to test optional arguments for Dataset constructor
    alt_lats = netcdf_file.createVariable('alt_lat', 'd', ('lat_dim',))
    alt_lons = netcdf_file.createVariable('alt_lon', 'd', ('lon_dim',))
    alt_times = netcdf_file.createVariable('alt_time', 'd', ('time_dim',))
    levels = netcdf_file.createVariable('level', 'd', ('level_dim',))
    values = netcdf_file.createVariable('value', 'd',
                                        ('time_dim',
                                         'level_dim',
                                         'lat_dim',
                                         'lon_dim')
                                        )

    # To latitudes and longitudes for five values
    latitudes_data = np.arange(5.)
    longitudes_data = np.arange(150., 155.)
    # Three months of data.
    times_data = np.arange(3)
    # Two levels
    levels_data = [100, 200]
    # Create 150 values
    values_data = np.array([i for i in range(150)])
    # Reshape values to 4D array (level, time, lats, lons)
    values_data = values_data.reshape(len(times_data), len(
        levels_data), len(latitudes_data), len(longitudes_data))

    # Ingest values to netCDF file
    latitudes[:] = latitudes_data
    longitudes[:] = longitudes_data
    times[:] = times_data
    alt_lats[:] = latitudes_data + 10
    alt_lons[:] = longitudes_data - 10
    alt_times[:] = times_data
    levels[:] = levels_data
    values[:] = values_data
    # Assign time info to time variable
    netcdf_file.variables['time'].units = 'months since 2001-01-01 00:00:00'
    netcdf_file.variables[
        'alt_time'].units = 'months since 2001-04-01 00:00:00'
    netcdf_file.variables['value'].units = 'foo_units'
    netcdf_file.close()
    return file_path


def create_invalid_dimensions_netcdf_file():
    """Create a temporary netCDF file with invalid dimensions for testing."""
    # To create the temporary netCDF file
    file_path = '/tmp/temporaryNetcdf.nc'
    netcdf_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
    # To create dimensions
    netcdf_file.createDimension('lat_dim', 5)
    netcdf_file.createDimension('lon_dim', 5)
    netcdf_file.createDimension('time_dim', 3)
    netcdf_file.createDimension('level_dim', 2)
    # To create variables
    latitudes = netcdf_file.createVariable('latitude', 'd', ('lat_dim',))
    longitudes = netcdf_file.createVariable('longitude', 'd', ('lon_dim',))
    times = netcdf_file.createVariable('time', 'd', ('time_dim',))
    levels = netcdf_file.createVariable('level', 'd', ('level_dim',))
    values = netcdf_file.createVariable('value',
                                        'd',
                                        ('level_dim',
                                         'time_dim',
                                         'lat_dim',
                                         'lon_dim')
                                        )
    # To latitudes and longitudes for five values
    flatitudes = list(range(0, 5))
    flongitudes = list(range(200, 205))
    # Three months of data
    ftimes = list(range(3))
    # Two levels
    flevels = [100, 200]
    # Create 150 values
    fvalues = np.array([i for i in range(150)])
    # Reshape values to 4D array (level, time, lats, lons)
    fvalues = fvalues.reshape(len(flevels), len(
        times), len(flatitudes), len(flongitudes))
    # Ingest values to netCDF file
    latitudes[:] = flatitudes
    longitudes[:] = flongitudes
    times[:] = ftimes
    levels[:] = flevels
    values[:] = fvalues
    # Assign time info to time variable
    netcdf_file.variables['time'].units = 'months since 2001-01-01 00:00:00'
    netcdf_file.close()
    return file_path


if __name__ == '__main__':
    unittest.main()
