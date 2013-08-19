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
import datetime
import numpy
import data_source.rcmed as rcmed


class test_rcmed(unittest.TestCase):


    def setUp(self):
        self.dataset_id = 2
        self.parameter_id = 15
        self.min_lat = 50
        self.max_lat = 70
        self.min_lon = 1
        self.max_lon = 15
        self.start_time = datetime.datetime(2002, 8, 1)
        self.end_time = datetime.datetime(2002, 10, 1)
        self.url = "http://rcmes.jpl.nasa.gov/query-api/query.php?"
        self.lats=numpy.arange(50.5, 70, 1)
        self.lons=numpy.arange(1.5, 15, 1)
        self.times=[datetime.datetime(2002,8,31) + datetime.timedelta(days=x) for x in range(0, 62)]
        self.times.remove(datetime.datetime(2002, 10, 20))
        self.times.remove(datetime.datetime(2002, 10, 21))
        #self.values


    def return_text(self, url):
        ##TODO: Replace the hard coded start and end time with variables.
        if url == self.url + "datasetId={0}&parameterId={1}&latMin={2}&latMax={3}&lonMin={4}&lonMax={5}&timeStart=20020801T0000Z&timeEnd=20021031T0000Z"\
                .format(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon):
            return open("parameter_dataset_text.txt")
        elif url == self.url + "&param_info=yes":
            return open("parameters_metadata_text.txt")
        else:
            raise Exceptption ("The URL is not acceptable.")


    def test_get_parameters_metadata(self):
        rcmed.urllib2.urlopen = self.return_text
        ##TODO: converting to string may not be very accurate, better approach is necessary
        self.assertEqual(str(rcmed.get_parameters_metadata()), open('get_parameters_metadata_output.txt','r').read())


    def test_parameter_dataset_latitudes(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assertTrue(numpy.allclose(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).lats, self.lats))


    def test_parameter_dataset_longitudes(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assertTrue(numpy.allclose(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).lons, self.lons))


    def test_parameter_dataset_times(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assertEqual(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).times, self.times)


if __name__ == '__main__':
    unittest.main()