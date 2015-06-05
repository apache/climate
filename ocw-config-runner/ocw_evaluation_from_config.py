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

import argparse
import logging

from configuration_parsing import is_config_valid
from evaluation_creation import generate_evaluation_from_config
from plot_generation import plot_from_config

import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)

def run_evaluation_from_config(config_file_path, ignore_config_errors=False):
    """ Run an OCW evaluation specified by a config file.

    :param config_file_path: The file path to a OCW compliant YAML file
        specifying how to run the evaluation. For additional information on 
        the valid options that you can set in the config please check the
        project wiki https://cwiki.apache.org/confluence/display/climate/home#'.
    :type config_file_path: :mod:`string`

    :param ignore_config_errors: When this is true configuration parsing errors
        will NOT interrupt the evaluation run. Note, it is very unlikely that
        you will want this value set. However it is possible that you will want
        to graph something that doesn't require a full evaluation run. This is
        provided for that situation.
    :type ignore_config_errors: :func:`bool`
    """
    config = yaml.load(open(config_file_path, 'r'))

    if not ignore_config_errors and not is_config_valid(config):
        logger.warning(
            'Unable to validate configuration file. Exiting evaluation. '
            'Please check documentation for config information.'
        )

        sys.exit(1)

    evaluation = generate_evaluation_from_config(config)

    if evaluation._evaluation_is_valid():
        evaluation.run()

    plot_from_config(evaluation, config)

if __name__ == '__main__':
    description = 'OCW Config Based Evaluation'
    epilog = 'Additional information at https://cwiki.apache.org/confluence/display/climate/home#'

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('config', help='Path to YAML config file for the evaluation')
    parser.add_argument('ignore_config_errors', nargs='?', default=False, type=bool)
    args = parser.parse_args()

    run_evaluation_from_config(args.config, args.ignore_config_errors)
