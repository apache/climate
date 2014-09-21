#
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
#

import urllib2

from ocw.esgf.constants import JPL_SEARCH_SERVICE_URL
from ocw.esgf.download import download
from ocw.esgf.logon2 import logon2
from ocw.esgf.search import SearchClient
import ocw.data_source.local as local

def load_dataset(dataset_id,
                 variable,
                 esgf_username,
                 esgf_password,
                 search_url=JPL_SEARCH_SERVICE_URL,
                 **additional_constraints):
    ''''''
    urls = _get_file_urls(url=search_url,
                          id=dataset_id,
                          variable=variable,
                          **additional_constraints)

    if len(urls) > 1:
        err = (
            "esgf.load_dataset: Unable to handle multi-file datasets. "
            "Feature coming soon ..."
        )
        raise ValueError(err)
    elif len(urls) == 0:
        err = (
            "esgf.load_dataset: No files found for specified dataset."
        )
        raise ValueError(err)

    # TODO: In the future, we need to combine multi-file datasets into a single
    # file and then load it. For now we're only handling a single file use case.
    _download_files(urls, esgf_username, esgf_password)
    return local.load_file('/tmp/' + urls[0].split('/')[-1], variable)

def _get_file_urls(**constraints):
    ''''''
    if 'url' in constraints:
        url = constraints['url']
        constraints.pop('url', None)
    else:
        url = ocw.esgf.constants.JPL_SEARCH_SERVICE_URL

    sc = SearchClient(searchServiceUrl=url, distrib=False)
    sc.setConstraint(**constraints)
    return sc.getFiles()

def _download_files(file_urls, username, password, download_directory='/tmp'):
    ''''''
    username = 'https://esg-datanode.jpl.nasa.gov/esgf-idp/openid/mjjoyce'
    password = '?pu}8gHM{2T2EB]jRX}TmKx6kCGEwPqfaP8aN8jGq8r4HDf82Y'
    try:
        logon2(username, password)
    except urllib2.HTTPError:
        raise ValueError('esgf._download_files: Invalid login credentials')

    for url in file_urls:
        download(url, toDirectory=download_directory)
