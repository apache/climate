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

    def __init__(self, reference, targets):
        '''Generate OCW Dataset objects from a variety of sources.

        Each keyword argument can be information for a dataset in dictionary
        form. For example:
        ``
        >>> reference = {'data_source':'rcmed', 'name':'cru', 'dataset_id':10,
                         'parameter_id':34}
        >>> targets = {'data_source':'local_multiple',
                       'path':'./data/CORDEX-Africa_data/AFRICA*pr.nc',
                       'variable':'pr'}
        >>> loader = DatasetLoader(reference, targets)
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

        :param reference: The reference dataset loader configuration.
        :type reference: :mod:`dict`

        :param targets: The target dataset loader configurations.
        :type targets: :mod:`dict` or list of mod:`dict`

        :raises KeyError: If an invalid argument is passed to a data source
        loader function.
        '''
        # Reference dataset config
        self.set_reference(reference)

        # Target dataset(s) config
        self.set_targets(targets)

        # Default loaders
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
        :type loader_func: :class:`callable`
        '''
        self._source_loader[source_name] = loader_func

    def add_target(self, **kwargs):
        '''
        A convenient means of adding a target dataset to the loader.
        :raises KeyError: If data_source is not specified.
        '''
        if 'data_source' not in kwargs:
            raise KeyError('Dataset configuration must contain a data_source.')
        self._target_config.append(kwargs)

    def add_targets(self, targets):
        '''
        A convenient means of adding multiple target datasets to the loader.

        :param targets: List of loader configurations for each target
        :type targets: List of :mod:`dict`

        :raises KeyError: If data_source is not specified.
        '''
        for target_config in targets:
            self.add_target(**target_config)

    def set_targets(self, targets):
        '''
        Reset the target dataset config.

        :param targets: List of loader configurations for each target
        :type targets: List of :mod:`dict`

        :raises KeyError: If data_source is not specified.
        '''
        # This check allows for the user to enter targets as one block or
        # as a list of separate blocks in their config files
        if not instanceof(targets, list):
            targets = [targets]
        self._target_config = []
        self.add_targets(targets)

    def set_reference(self, **kwargs):
        '''
        Reset the reference dataset config.
        :raises KeyError: If data_source is not specified.
        '''
        if 'data_source' not in kwargs:
            raise KeyError('Dataset configuration must contain a data_source.')
        self._reference_config = kwargs

    def load_datasets(self):
        '''
        Loads the datasets from the given loader configurations.
        '''
        # Load the reference dataset
        self.reference_dataset = self._load(**self._reference_config)

        # Ensure output is clear if loading is performed more than once to
        # prevent duplicates.
        self.target_datasets = []

        # Load the target datasets
        for loader_params in self._target_config
            output = self._load(**loader_params)

                # Need to account for the fact that some loaders return lists
                # of OCW Dataset objects instead of just one
                if isinstance(target_dataset, list):
                    self.target_datasets.extend(output)
                else:
                    self.target_datasets.append(output)

    def _load(self, **kwargs):
        '''
        Generic dataset loading method.
        '''
        # Extract the data source
        data_source = kwargs.pop('data_source')

        # Find the correct loader function for the given data source
        loader_func = self._source_loaders[data_source]

        # The remaining kwargs should be specific to the loader
        output = loader_func(**kwargs)

        # Preserve data_source info for later use
        kwargs['data_source'] = data_source
        return output
