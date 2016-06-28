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

import os.path
from setuptools import find_packages, setup

# Package data
# ------------
_author       = 'Apache Open Climate Workbench'
_authorEmail  = 'dev@climate.apache.org'
_classifiers  = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Python Modules',
]
_description  = 'Apache Open Climate Workbench'
_downloadURL  = 'http://pypi.python.org/pypi/ocw/'
_requirements = []
_keywords     = ['climate analysis', 'workbench', 'rebinning', 'metrics', 'computation', 'visualization']
_license      = 'Apache License, Version 2.0'
_long_description    = 'The Apache Open Climate Workbench provides tools for the evaluation and analysis of climate models.'
_name         = 'ocw'
_namespaces   = []
_testSuite    = 'ocw.tests'
_url          = 'http://climate.apache.org/'
_version      = '1.1.0'
_zipSafe      = True

# Setup Metadata
# --------------

def _read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_header = '*' * len(_name) + '\n' + _name + '\n' + '*' * len(_name)
_longDescription = '\n\n'.join([
    _header,
    _read('README.md')
])
open('doc.txt', 'w').write(_longDescription)

setup(
    author=_author,
    author_email=_authorEmail,
    classifiers=_classifiers,
    description=_description,
    download_url=_downloadURL,
    include_package_data=True,
    install_requires=_requirements,
    keywords=_keywords,
    license=_license,
    long_description=_longDescription,
    name=_name,
    namespace_packages=_namespaces,
    packages=find_packages(),
    test_suite=_testSuite,
    url=_url,
    version=_version,
    zip_safe=_zipSafe,
)
