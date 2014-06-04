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

export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

help()
{
cat << ENDHELP

Easy OCW assists with the building of the Apache Open Climate Workbench and its dependencies

Flags:
    -h  Display this help message.
    -e  Install and configure a virtualenv environment before installation.
    -q  Quiet install. User prompts are removed (when possible).

It is recommended that you pass -e when running this script. If you don't, parts
of this installation will pollute your global Python install. If you're unsure,
pass -e just to be safe!

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

WITH_VIRTUAL_ENV=0
WITH_HOMEBREW=0
WITH_INTERACT=1
INIT_PWD=$PWD
while getopts ":h :e :q" FLAG
do
    case $FLAG in
        h)
            help
            exit 1
            ;;
        e)
            WITH_VIRTUAL_ENV=1
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

if [ $WITH_VIRTUAL_ENV != 1 ]; then
cat << VIRTUALENV_WARNING
It is highly recommended that you allow Easy OCW to install the dependencies
into a virtualenv environment to ensure that your global Python install is
not affected. If you're unsure, you should pass the -e flag
to this script. If you aren't concerned, or you want to create your own
virtualenv environment, then feel free to ignore this message.

VIRTUALENV_WARNING
fi

read -p "Press [ENTER] to begin installation ..."
fi

header "Checking for pip ..."
if [ ! command -v pip >/dev/null 2>&1 ]; then
    task "Unable to locate pip."
    task "Installing Distribute"
    curl http://python-distribute.org/distribute_setup.py | python >> install_log
    subtask "done"

    task "Installing Pip"
    curl -O http://pypi.python.org/packages/source/p/pip/pip-1.2.1.tar.gz >> install_log
    tar xzf pip-1.2.1.tar.gz >> install_log
    cd pip-1.2.1/
    python setup.py install >> install_log
    subtask "done"
fi

if [ $WITH_VIRTUAL_ENV == 1 ]; then
    header "Setting up a virtualenv ..."

    # Check if virtualenv is installed. If it's not, we'll install it for the user.
    if ! command -v virtualenv >/dev/null 2>&1; then
        task "Installing virtualenv ..."
        pip install virtualenv >> install_log
        subtask "done"
    fi

    # Create a new environment for OCW work
    task "Creating a new environment in ~/ocw..."
    cd ~
    virtualenv ocw >> install_log
    source ~/ocw/bin/activate >> install_log
    cd $INIT_PWD
    subtask "done"
fi

header "Installing conda for package management ..."

pip install conda >> install_log
conda init >> install_log


header "Installing dependencies with conda ..."
echo | conda install --file ocw-conda-dependencies.txt

# We only use conda for the annoying dependencies like numpy,
# scipy, matplotlib, and basemap. For everything else, we stick
# with pip.
header "Installing additional Python packages"
pip install -r ocw-pip-dependencies.txt >> install_log


if [ $WITH_VIRTUAL_ENV == 1 ]; then
    echo "***POST INSTALLATION NOTE***
To make it easier to change into the 'ocw' virtualenv add the
following alias to your ~/.bash_profile

    alias ocw='source ~/ocw/bin/activate ~/ocw/'

When you want to use ocw in the future, you just have to type 'ocw'
in your terminal."
fi

