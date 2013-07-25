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
from metrics import Metric

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
        '''Default Evaluation constructor.'''
        #: The reference dataset.
        self.ref_dataset = None
        #: The target dataset(s) which should each be compared with 
        #: the reference
        #: dataset when the evaluation is run.
        self.target_datasets = []
        #: The list of "binary" metrics (A metric which takes two Datasets) 
        #: that the Evaluation should use.
        self.metrics = []
        #: The list of "unary" metrics (A metric which takes one Dataset) that
        #: the Evaluation should use.
        self.unary_metrics = []

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

        :raises ValueError: If the metric to add isn't a class that inherits \
                from metrics.Metric.
        '''
        if not isinstance(metric, Metric):
            error = (
                "Cannot add a metric that doesn't inherit from Metric. "
                "Please consult the documentation for additional help."
            )
            logging.error(error)
            raise TypeError(error)

        if metric.isUnary:
            self.unary_metrics.append(metric)
        else:
            self.metrics.append(metric)

    def add_metrics(self, metrics):
        '''Add mutliple metrics to the Evaluation.

        A metric is a function of the form:
            f(ref_dataset, target_dataset)

        :param metrics: The list of metric functions to add to the Evaluation.
        :type metrics: List of functions

        :raises ValueError: If a metric to add isn't a class that inherits \
                from metrics.Metric.
        '''
        for metric in metrics:
            self.add_metric(metric)


    def run(self):
        '''Run the evaluation.'''
        if not self._evaluation_is_valid():
            error = "The evaluation is invalid. Check the docs for help."
            logging.warning(error)
            return

        # Results are saved as a list of lists of the form
        # [
        #   [ // The results for the first metric
        #     The results of first target dataset,
        #     The results of second target dataset,
        #     The results of third target dataset
        #   ]
        #   [ // The results for the second metric
        #     The results of first target dataset,
        #     The results of second target dataset,
        #     The results of third target dataset
        #   ]
        # ]
        if should_run_regular_metrics():
            self.results = []
            for target in self.target_datasets:
                self.results.append([])
                for metric in self.metrics:
                    run_result = [metric.run(self.ref_dataset, taget)]
                    self.results[-1].append(run_result)

        if should_run_unary_metrics():
            self.unary_results = []

            for metric in self.unary_metrics:
                self.unary_results.append([])
                # Unary metrics should be run over the reference Dataset also
                if self.ref_dataset:
                    self.unary_results[-1].append(metric.run(ref_dataset))

                for target in self.target_datasets:
                    self.unary_results[-1].append(metric.run(target))


    def _evaluation_is_valid(self):
        '''Check if the evaluation is well-formed.
        
        * If there are no metrics or no datasets it's invalid.
        * If there is a unary metric there must be a reference dataset or at
            least one target dataset.
        * If there is a regular metric there must be a reference dataset and
            at least one target dataset.
        '''
        run_reg = should_run_regular_metrics()
        run_unary = should_run_unary_metrics()
        reg_valid = self.ref_dataset != None and len(self.target_datasets) > 0
        unary_valid = self.ref_dataset != None or len(self.target_datasets) > 0

        if run_reg and run_unary:
            return reg_valid and unary_valid
        elif run_reg:
            return reg_valid
        elif run_unary:
            return unary_valid
        else:
            return false
