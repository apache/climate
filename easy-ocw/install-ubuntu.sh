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

help()
{
cat << ENDHELP

Easy OCW assists with the building of the Apache Open Climate Workbench and 
its dependencies.

Flags:
    -h  Display this help message.
    -q  Quiet install. User prompts are removed (when possible).

N.B. This install script has been tested against Ubuntu 12.04 and 14.04.
Please report problems with this script to dev@climate.apache.org
ENDHELP
}

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

echo
echo "---------------------------------------------------------------------------"
echo "                         Welcome to Easy OCW"
echo "---------------------------------------------------------------------------"
echo

WITH_HOMEBREW=0
WITH_INTERACT=1

# Find absolute path to the easy-ocw directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR
ocw_path="$DIR/../climate"

while getopts ":h :e :q" FLAG
do
    case $FLAG in
        h)
            help
            exit 1
            ;;
        q)
            WITH_INTERACT=0
            ;;
        ?)
            help
            exit 1
            ;;
    esac
done

if [ $WITH_INTERACT == 1 ]; then
cat << ENDINTRO
A number of dependencies for OCW will now be installed. Please check the wiki
for a complete list of dependencies. Additionally, please read the wiki for
useful installation guidelines and information that may be pertinent to your
situation. All of this can be found at http://s.apache.org/3p2
ENDINTRO

fi

echo "Easy-OCW script logs" > install_log
header "Checking for pip ..."
command -v pip >/dev/null 2>&1 || { 
    task "Unable to locate pip."
    task "Installing Pip"
    sudo apt-get -y install python-pip >> install_log 2>&1
    subtask "done"
}

# Install Continuum Analytics Miniconda Python distribution. This gives
# almost all the dependencies that OCW needs in a single, easy to
# install package.

header "Installing Miniconda Python distribution ..."
echo
echo "*** NOTE *** When asked to update your PATH, you should respond YES and please do not change the default installation directory"
read -p "Press [ENTER] to continue ..."

MACHINE_TYPE=`uname -m`
if [ ${MACHINE_TYPE} == 'x86_64' ]; then
	link="https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh"
else
	link="https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86.sh"
fi

header "Checking for conda ..."
command -v conda >/dev/null 2>&1 || { 
    task "Unable to locate conda."
    if ! [ -f Miniconda-latest-linux.sh ]; then
		task "Downloading Miniconda ..."
		wget -O Miniconda-latest-linux.sh $link >> install_log 2>&1
		subtask "done"
    fi
	task "Installing ..."
	bash Miniconda-latest-linux.sh
	subtask "done"
}

task "Installing python-dev"
sudo apt-get -y install python-dev >> install_log 2>&1
subtask "done"
header "Part 1/2 of installation completed. Please start a new terminal and execute conda-install.sh script."
