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
    Metric - Abstract Base Class from which all metrics must inherit.
'''

from abc import ABCMeta, abstractmethod
import ocw.utils as utils
import numpy
from scipy import stats

class Metric(object):
    '''Base Metric Class'''
    __metaclass__ = ABCMeta


class UnaryMetric(Metric):
    '''Abstract Base Class from which all unary metrics inherit.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, target_dataset):
        '''Run the metric for a given target dataset.

        :param target_dataset: The dataset on which the current metric will
            be run.

        :returns: The result of evaluating the metric on the target_dataset.
        '''


class BinaryMetric(Metric):
    '''Abstract Base Class from which all binary metrics inherit.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, ref_dataset, target_dataset):
        '''Run the metric for the given reference and target datasets.

        :param ref_dataset: The Dataset to use as the reference dataset when
            running the evaluation.
        :type ref_dataset: Dataset
        :param target_dataset: The Dataset to use as the target dataset when
            running the evaluation.

        :returns: The result of evaluation the metric on the reference and 
            target dataset.
        '''


class Bias(BinaryMetric):
    '''Calculate the bias between a reference and target dataset.'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the bias between a reference and target dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The difference between the reference and target datasets.
        :rtype: Numpy Array
        '''
        return ref_dataset.values - target_dataset.values


class TemporalStdDev(UnaryMetric):
    '''Calculate the standard deviation over the time.'''

    def run(self, target_dataset):
        '''Calculate the temporal std. dev. for a datasets.

        .. note::
           Overrides UnaryMetric.run()

        :param target_dataset: The target_dataset on which to calculate the 
            temporal standard deviation.
        :type target_dataset: Dataset

        :returns: The temporal standard deviation of the target dataset
        :rtype: Numpy Array
        '''
        return target_dataset.values.std(axis=0, ddof=1)


class SpatialStdDevRatio(BinaryMetric):
    '''Calculate the ratio of spatial standard deviation (model standard
          deviation)/(observed standard deviation)'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the ratio of spatial std. dev. between a reference and
            target dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The ratio of standard deviation of the reference and target
            dataset.
        '''

        # This is calcClimYear function for ref_dataset
        reshaped_ref_data = utils.reshape_monthly_to_annually(ref_dataset)
        ref_t_series = reshaped_ref_data.mean(axis=1)
        ref_means = ref_t_series.mean(axis=0)

        # This is calcClimYear function for target_dataset
        reshaped_target_data = utils.reshape_monthly_to_annually(target_dataset)
        target_t_series = reshaped_target_data.mean(axis=1)
        target_means = target_t_series.mean(axis=0)

        return numpy.std(ref_means) / numpy.std(target_means)


class PatternCorrelation(BinaryMetric):
    '''Calculate the spatial correlation'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the spatial correlation between a reference and target dataset.
            Using: scipy.stats.pearsonr

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The spatial correlation between a reference and target dataset.
        '''
        # This is calcClimYear function for ref_dataset
        reshaped_ref_data = utils.reshape_monthly_to_annually(ref_dataset)
        ref_t_series = reshaped_ref_data.mean(axis=1)
        ref_means = ref_t_series.mean(axis=0)

        # This is calcClimYear function for target_dataset
        reshaped_target_data = utils.reshape_monthly_to_annually(target_dataset)
        target_t_series = reshaped_target_data.mean(axis=1)
        target_means = target_t_series.mean(axis=0)

        pattern_correlation, p_value = stats.pearsonr(target_means.flatten(),ref_means.flatten())
        return pattern_correlation, p_value

class MeanBias(BinaryMetric):
    '''Calculate the mean bias'''

    def run(self, ref_dataset, target_dataset, absolute=False):
        '''Calculate the mean bias between a reference and target dataset over all time.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The the mean bias between a reference and target dataset over all time.
        '''

        diff = ref_dataset.values - target_dataset.values
        if absolute:
            diff = abs(diff)
        mean_bias = diff.mean(axis=0)

        return mean_bias

class SeasonalSpatialStdDevRatio(BinaryMetric):
    '''Calculate the ratio of spatial standard deviation (model standard
          deviation)/(observed standard deviation)'''

    def __init__(self, month_start=1, month_end=12):
        self.month_start = month_start
        self.month_end = month_end

    def run(self, ref_dataset, target_dataset):
        '''Calculate the ratio of spatial std. dev. between a reference and
            target dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The ratio of standard deviation of the reference and target
            dataset.
        '''

        ref_t_series, ref_means = utils.calc_climatology_season(self.month_start, self.month_end, ref_dataset)
        target_t_series, target_means = utils.calc_climatology_season(self.month_start, self.month_end, target_dataset)

        return numpy.std(ref_means) / numpy.std(target_means)


class SeasonalPatternCorrelation(BinaryMetric):
    '''Calculate the spatial correlation'''

    def __init__(self, month_start=1, month_end=12):
        self.month_start = month_start
        self.month_end = month_end

    def run(self, ref_dataset, target_dataset):
        '''Calculate the spatial correlation between a reference and target dataset.
            Using: scipy.stats.pearsonr

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: Dataset.
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: Dataset.

        :returns: The spatial correlation between a reference and target dataset.
        '''
        ref_t_series, ref_means = utils.calc_climatology_season(self.month_start, self.month_end, ref_dataset)
        target_t_series, target_means = utils.calc_climatology_season(self.month_start, self.month_end, target_dataset)

        pattern_correlation, p_value = stats.pearsonr(target_means.flatten(),ref_means.flatten())
        return pattern_correlation, p_value
