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
    Evaluation - Container for running an evaluation
'''

import logging

class Evaluation:
    '''Container for running an evaluation

    An *evaluation* is the comparison of one or model datasets against 
    some reference dataset. Metrics are added to an Evaluation and all are 
    run with the base dataset and each of the target datasets in turn.  The 
    results of running the evaluation are stored for future use.

    In order for an Evaluation to be valid at least one Dataset must be added
    as the reference Dataset, one Dataset must be added as a target Dataset, 
    and one metric function must be added.
    '''

    def __init__(self):
        '''Default Evaluation constructor.
        '''
        self.ref_dataset = None
        self.target_datasets = []
        self.metrics = []

    def add_ref_dataset(self, ref_dataset):
        '''Add reference Dataset to the Evaluation.

        The reference dataset is the base on which all other datasets are 
        compared.

        :param ref_dataset: The reference dataset to add to the Evaluation.
        :type ref_dataset: Dataset
        '''
        self.ref_dataset = ref_dataset

    def add_dataset(self, target_dataset):
        '''Add a Dataset to the Evaluation.

        A target Dataset is compared against the reference dataset when the 
        Evaluation is run with one or more metrics.

        :param target_dataset: The target Dataset to add to the Evaluation.
        :type target_dataset: Dataset
        '''
        self.target_datasets.append(target_dataset)

    def add_datasets(self, target_datasets):
        '''Add multiple Datasets to the Evaluation.

        :param target_datasets: The list of datasets that should be added to 
            the Evaluation.
        :type target_datasets: List of Dataset objects
        '''
        self.target_datasets += target_datasets

    def add_metric(self, metric):
        '''Add a metric to the Evaluation.

        A metric is a function of the form:
            f(ref_dataset, target_dataset)

        It performs some operation on the reference and target dataset
        and returns the resulting data.

        :param metric: The metric function to add to the Evaluation.
        :type metric: function
        '''
        self.metrics += metric

    def add_metrics(self, metrics):
        '''Add mutliple metrics to the Evaluation.

        A metric is a function of the form:
            f(ref_dataset, target_dataset)

        :param metrics: The list of metric functions to add to the Evaluation.
        :type metrics: List of functions
        '''
        self.metrics += metrics

    def run(self):
        '''Run the evaluation.'''
        if not self._evaluation_is_valid():
            error = "The evaluation is invalid. Check the docs for help."
            logging.warning(error)
            return

        # All pairs of (ref_dataset, target_dataset) must be run with
        # each available metric.
        for target in self.target_datasets:
            for metric in self.metrics:
                # Should we pass the calling of the metric off to another 
                # function? This might make dataset access cleaner instead
                # of doing it inline.
                #result += _apply_metric(metric, self.ref_dataset, target)
                #self.results += result

                # Should a metric expect to take Dataset objects or should
                # it expect to take data (aka numpy) arrays?
                #self.results += metric(self.ref_dataset, target)

                # If it expects the actual data
                #self.results += metric(self.ref_dataset.value,
                #                       target.value)
                pass

    def _evaluation_is_valid(self):
        '''Check if the evaluation is well-formed.
        
        A valid evaluation will have:
            * Exactly one reference Dataset
            * One or more target Datasets
            * One or more metrics
        '''
        pass
