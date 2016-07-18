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

'''
Classes:
    DatasetLoader - Generate OCW Dataset objects from a variety of sources.
'''

import ocw.data_source.local as local
import ocw.data_source.esgf as esgf
import ocw.data_source.rcmed as rcmed
import ocw.data_source.dap as dap

class DatasetLoader:
    '''Generate OCW Dataset objects from a variety of sources.'''

    def __init__(self, **kwargs):
        '''Generate OCW Dataset objects from a variety of sources.

        Each keyword argument can be information for a dataset in dictionary
        form. For example:
        ``
        >>> reference = {'data_source':'rcmed', 'name':'cru', 'dataset_id':10,
                         'parameter_id':34}
        >>> targets = {'data_source':'local_multiple',
                       'path':'./data/CORDEX-Africa_data/AFRICA*pr.nc',
                       'variable':'pr'}
        >>> loader = DatasetLoader(reference=reference, targets=targets)
        ``

        Or more conveniently if the loader configuration is defined in a
        yaml file named config_file (see RCMES examples):
        ``
        >>> import yaml
        >>> config = yaml.load(open(config_file))
        >>> loader = DatasetLoader(**config['datasets'])
        ``

        As shown in the first example, the dictionary for each keyword argument
        should contain a data source and parameters specific to the loader for
        that data source. Once the configuration is entered, the datasets may be
        loaded using:
        ``
        >>> loader.load_datasets()
        >>> target_datasets = loader.target_datasets
        ``

        If ``reference`` is entered as a keyword argument, then it may be
        accesed from:
        ``
        >>> reference_dataset = loader.reference_dataset
        ``

        Additionally, each dataset must have a ``data_source`` keyword. This may
        be one of the following:
        * ``'local'`` - A single dataset file in a local directory
        * ``'local_split'`` - A single dataset split accross multiple files in a
                              local directory
        * ``'local_multiple'`` - Multiple datasets in a local directory
        * ``'esgf'`` - Download the dataset from the Earth System Grid
                       Federation
        * ``'rcmed'`` - Download the dataset from the Regional Climate Model
                        Evaluation System Database
        * ``'dap'`` - Download the dataset from an OPeNDAP URL

        Users who wish to download datasets from sources not described above
        may define their own custom dataset loader function and incorporate it
        as follows:
        >>> loader.add_source_loader('my_source_name', my_loader_func)

        :raises KeyError: If an invalid argument is passed to a data source
        loader function.
        '''
        self.reference_dataset = None
        self.target_datasets = []
        self._config = kwargs
        self._source_loaders = {
                    'local':local.load,
                    'local_split':local.load_dataset_from_multiple_netcdf_files
                    'local_multiple':local.load_multiple_files,
                    'esgf':esgf.load_dataset,
                    'rcmed':parameter_dataset,
                    'dap':dap.load
                    }

    def add_source_loader(self, source_name, loader_func):
        '''
        Add a custom source loader.

        :param source_name: The name of the data source.
        :type source_name: :mod:`string`

        :param loader_func: Reference to a custom defined function. This should
        return an OCW Dataset object.
        :type loader_func: :mod:`callable`
        '''
        self._source_loader[source_name] = loader_func


    def set_config(self, **kwargs):
        '''
        Change loader config if necessary. See class docstring for more info.
        '''
        self._config = kwargs

    def load_datasets(self):
        '''
        Loads the datasets from the given loader configuration.
        '''
        for dataset_evaltype, dataset_params in self._config.iteritems():
            data_source = dataset_params.pop('data_source'):
            load_func = self._source_loaders[data_source]
            if dataset_evaltype == 'reference':
                self.reference_dataset = load_func(**dataset_params)
            else:
                target_dataset = load_func(**dataset_params)
                self.target_datasets.extend(target_dataset)
