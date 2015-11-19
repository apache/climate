#!/bin/bash
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

# Check if the user has conda installed. If not, we'll install Miniconda for them
command -v conda >/dev/null 2>&1 || {
    echo "Couldn't find conda. Attempting to install Miniconda"
    OS=`uname -s`

    if [ "${OS}" == "Darwin" ]; then
        curl https://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh -o /tmp/miniconda.sh
        bash /tmp/miniconda.sh
    elif [ "${OS}" == "Linux" ]; then
        if [ `uname -m` == "x86_64" ]; then
            curl https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -o /tmp/miniconda.sh
        else
            curl https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86.sh -o /tmp/miniconda.sh
        fi
        bash /tmp/miniconda.sh
    else
        echo "Unable to identify your OS. Please report this to the OCW List"
        echo "dev@climate.apache.org"
    fi

    source ~/.bashrc
}

echo "Creating conda environment from ocw environment file"
conda env create -f conda_environment.txt
