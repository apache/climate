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

''' Services for interacting with NASA JPL's PODAAC Database. '''

from podaac.podaac_utils import PodaacUtils
from bottle import Bottle

podaac_app = Bottle()
podaac_utils = PodaacUtils()

@podaac_app.route('/datasets/', methods=['GET'])
def get_observation_dataset_data():
    ''' Return a list of dataset information from JPL's PODAAC.
    '''
    r = podaac_utils.list_available_granule_search_level2_dataset_ids()
    return r
