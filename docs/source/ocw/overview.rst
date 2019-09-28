Overview
========

The Apache Open Climate Workbench (OCW) toolkit aims to make climate scientists' lives easier by providing a standardized workflow for manipulating datasets and generating metrics from them. This document provides an overview of the OCW components involved in this workflow, along with explanations of how to use them.

A typical OCW script performs the following steps:

1. Load one or more **datasets** from a variety of sources
2. Perform manipulations on the datasets (subset, temporal/spatial rebin, etc.)
3. Load relevant **metrics** to evaluate for the datasets
4. Instantiate an **evaluation** object that evaluates specified metrics for specified datasets
5. Plot the evaluation's results

Common Data Abstraction
-----------------------

The :class:`dataset.Dataset` class is the OCW's primary data abstraction. It facilitates the uniform handling of data throughout the toolkit and provides a few useful helper functions, such as :func:`dataset.Dataset.spatial_boundaries` and :func:`dataset.Dataset.temporal_boundaries`. Creating a new dataset object is straightforward, but generally you'll want to use an OCW **data source** to load the data for you.

Data Sources
------------

OCW data sources allow you to easily load :class:`dataset.Dataset` objects from a variety of places. These data sources help with step 1 of the workflow described above.

Most OCW data sources primarly use the NetCDF file format. For instance, the :mod:`local`, :mod:`dap`, and :mod:`esgf` data sources support loading only NetCDF files from your local machine, an OpenDAP URL, and the ESGF, respectively.

Certain data sources, such as :mod:`rcmed`, point to externally supported data sources. In the case of the RCMED data source, the Regional Climate Model Evaluation Database is run by NASA's Jet Propulsion Laboratory.

Adding support for a new data source is straightforward. The only API requirement is that every data source must return a valid :class:`dataset.Dataset` object. Please feel free to send patches for adding new data sources.

Here's a simple example that uses the :mod:`local` data source to load a NetCDF file from your local machine::

>>> import ocw.data_source.local as local
>>> ds = local.load_file('/tmp/some_dataset.nc', 'SomeVarInTheDataset')

Dataset Manipulations
---------------------

All :class:`dataset.Dataset` manipulations are handled by the :mod:`dataset_processor` module. Typically, an evaluation includes calls to :func:`dataset_processor.subset`, :func:`dataset_processor.spatial_regrid`, and :func:`dataset_processor.temporal_rebin` to ensure that the datasets can actually be compared.

Most :mod:`dataset_processor` functions take in a :class:`dataset.Dataset` object (along with other parameters), perform relevant processing on the data, and return a new :class:`dataset.Dataset` object. The original dataset object is never manipulated in the process.

Common Manipulations
~~~~~~~~~~~~~~~~~~~~

**Subsetting** is a great way to speed up your processing and keep useless data out of your plots. The following example uses a :class:`dataset.Bounds` object to restrict a dataset to a particular region of interest::

>>> import ocw.dataset_processor as dsp
>>> new_bounds = Bounds(min_lat, max_lat, min_lon, max_lon, start_time, end_time)
>>> knmi_dataset = dsp.subset(knmi_dataset, new_bounds)

**Temporally re-binning** a dataset is useful when your data's time step is too fine-grained for your use case. For example, if you want to visualize a yearly trend but are working with daily data, you can make the following call to adjust your dataset::

>>> knmi_dataset = dsp.temporal_rebin(knmi_dataset, datetime.timedelta(days=365))

It is critical for a collection of datasets to be on the same lat/lon grid before they are compared. That's where **spatial re-gridding** comes in handy. The following example re-grids a dataset onto a 1-degree lat/lon grid within the bounds specified in the example above::

>>> new_lons = np.arange(min_lon, max_lon, 1)
>>> new_lats = np.arange(min_lat, max_lat, 1)
>>> knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)

Metrics
-------

Metrics are the backbone of an evaluation. The toolkit's :mod:`metrics` module provides a number of (hopefully) useful "default" metrics.

In general, it's uncommon to run a metric outside of an evaluation, however you can do so manually::

>>> import ocw.metrics
>>> # Load 2 datasets
>>> bias = ocw.metrics.Bias()
>>> print(bias.run(dataset1, dataset2))

While this can be useful for one-off situations, it's far more likely that you'll need to run a number of metrics over a number of datasets. This is where running metrics within an evaluation comes in (covered in greater detail below).

Creating Custom Metrics
~~~~~~~~~~~~~~~~~~~~~~~

The toolkit supports two "types" of metrics: unary metrics and binary metrics.

* **Unary metrics** act on a single dataset and return a result.
* **Binary metrics** act on two datasets (a **target** and a **reference**) and return a result.

This dichotomy is helpful to know if you decide to create your own custom metric. To do so, simply create a new class that inherits from either the unary or binary base class and overrides its ``run`` function.

The following snippet shows the implementation of the default ``Bias`` metric. If you need further assistance with creating custom metrics, be sure to email the project's mailing list::

>>> class Bias(BinaryMetric):
>>>     '''Calculate the bias between a reference and target dataset.'''
>>> 
>>>     def run(self, ref_dataset, target_dataset):
>>>         '''Calculate the bias between a reference and target dataset.
>>> 
>>>         .. note::
>>>            Overrides BinaryMetric.run()
>>> 
>>>         :param ref_dataset: The reference dataset to use in this metric run.
>>>         :type ref_dataset: ocw.dataset.Dataset object
>>>         :param target_dataset: The target dataset to evaluate against the
>>>             reference dataset in this metric run.
>>>         :type target_dataset: ocw.dataset.Dataset object
>>> 
>>>         :returns: The difference between the reference and target datasets.
>>>         :rtype: Numpy Array
>>>         '''
>>>         return ref_dataset.values - target_dataset.values

Although this code might look intimidating at first, most of it is documentation markup. The following (much simpler) snippet is the same code with documentation markup removed::

>>> # Our new Bias metric inherits from the Binary Metric base class
>>> class Bias(BinaryMetric):
>>>     # Since our new metric is a binary metric, we need to override
>>>     # the run funtion in the BinaryMetric base class.
>>>     def run(self, ref_dataset, target_dataset):
>>>         # To implement the bias metric we simply return the difference
>>>         # between the reference and target dataset's values arrays.
>>>         return ref_dataset.values - target_dataset.values

If you create a custom metric, **do not modify any datasets that are passed into it**. If you do, you will probably cause unexpected results in subsequent steps of the evaluation. If you need to manipulate data, first copy it and perform all manipulations on the copy. Leave the original dataset alone!

Handling an Evaluation
----------------------

When you have a large collection of datasets and a large collection of metrics to run on them, you should encapsuate those operations in an :class:`evaluation.Evaluation` to ensure consistency and prevent errors. An evaluation ensures that all of the metrics you choose are evaluated for all valid combinations of the datasets that you specify. Consider the following simple example::

>>> import ocw.evaluation as eval
>>> import ocw.data_source.local as local
>>> import ocw.metrics as metrics
>>> 
>>> # Load a few datasets
>>> ref_dataset = local.load_file(...)
>>> target1 = local.load_file(...)
>>> target2 = local.load_file(...)
>>> target_datasets = [target1, target2]
>>>
>>> # Do some dataset manipulations here such as subsetting and regridding
>>>
>>> # Load a few metrics
>>> bias = metrics.Bias()
>>> tstd = metrics.TemporalStdDev()
>>> metrics = [bias, tstd]
>>>
>>> new_eval = eval.Evaluation(ref_dataset, target_datasets, metrics)
>>> new_eval.run()
>>> print(new_eval.results)
>>> print(new_eval.unary_results)

First, we load the datasets to process and perform any necessary manipulations (which are omitted for brevity). Then, we load the metrics that we want to run (namely, ``Bias`` and ``TemporalStdDev``). We then load our evaluation object::

>>> new_eval = eval.Evaluation(ref_dataset, target_datasets, metrics)

Note that the evaluation takes a single **reference** dataset (``ref_dataset``) and a list of **target** datasets (``target_datasets``). This is necessary for the processing of any binary metrics. Every binary metric is run against every possible reference-target combination included in the evaluation.

Note also that one of the metrics included in the evaluation (:class:`metrics.TemporalStdDev`) is a unary metric. Unary metrics are run against *every* dataset included in the evaluation (reference and target alike).

Evaluation Results
~~~~~~~~~~~~~~~~~~

Evaluation objects store the results of metrics processing in two lists:

* The ``results`` list is a multidimensional array that holds the results of all binary metrics.
* The ``unary_results`` list is a list that holds the results of all unary metrics.

In the example above, one could theoretically replicate the resulting structure of these lists with the following code::

>>> results = [
>>>     # Results for target1
>>>     [
>>>         bias.run(ref_dataset, target1)
>>>         # If there were other binary metrics, the results would be here.
>>>     ],
>>>     # Results for target2
>>>     [
>>>         bias.run(ref_dataset, target2)
>>>         # If there were other binary metrics, the results would be here.
>>>     ]
>>> ]
>>>
>>> unary_results = [
>>>     # Results for TemporalStdDev
>>>     [
>>>         tstd(ref_dataset),
>>>         tstd(target1),
>>>         tstd(target2)
>>>     ]
>>>     # If there were other unary metrics, the results would be in a list here.
>>> ]

Plotting
--------

Plotting the results of an evaluation can be complicated. Luckily, we have `pretty good documentation <https://cwiki.apache.org/confluence/display/CLIMATE/Guide+to+Plotting+API>`_ on the project wiki to help you out. There are also fairly simple examples in the project's ``examples`` folder, such as the following::

>>> # Let's grab the values returned for bias.run(ref_dataset, target1)
>>> results = bias_evaluation.results[0][0]
>>>
>>> Here's the same lat/lons we used earlier when we were re-gridding
>>> lats = new_lats
>>> lons = new_lons
>>> fname = 'My_Test_Plot'
>>>  
>>> plotter.draw_contour_map(results, lats, lons, fname)

The above snippet plots a contour map called ``My_Test_Plot`` for the requested bias metric run.
