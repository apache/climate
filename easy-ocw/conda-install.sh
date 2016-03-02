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

header()
{
    echo
    echo $1
}

task()
{
    echo " - " $1
}

subtask()
{
    echo "     " $1
}

# Find absolute path to the easy-ocw directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

header "Installing dependencies via conda"
task "Reading and installing from ocw-conda-dependencies.txt (This might take some time"
conda install --file ocw-conda-dependencies.txt
subtask "done"

# Install miscellaneous Python packages needed for OCW. Some of these
# can be installed with Conda, but since none of them have an annoying
# compiled component we just installed them with Pip.
header "Installing additional Python packages"
task "Reading and installing from ocw-pip-dependencies.txt (Please wait...)"
pip install -r ocw-pip-dependencies.txt
subtask "done"

header "Installing ocw module"
cd ..
# Open new and install OCW
python setup.py install 
subtask "finished installing ocw module"

header "Part 2/2 of Installation completed. Please close the terminal and start to new one for the changes to take effect"
header "For any issues with installation please contact dev@climate.apache.org"
