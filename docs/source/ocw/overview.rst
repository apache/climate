Overview
========

The Apache Open Climate Workbench toolkit aims to provide a suit of tools to make Climate Scientists lives easier. It does this by providing tools for loading and manipulating datasets, running evaluations, and plotting results. Below is a breakdown of many of the OCW components with an explanation of how to use them. An OCW evaluation usually has the following steps:

1. Load one or more datasets
2. Perform dataset manipulations (subset, temporal/spatial rebin, etc.)
3. Load various metrics
4. Instantiate and run the evaluation
5. Plot results

Common Data Abstraction
-----------------------

The OCW :class:`dataset.Dataset` class is the primary data abstraction used throughout OCW. It facilitates the uniform handling of data throughout the toolkit and provides a few useful helper functions such as :func:`dataset.Dataset.spatial_boundaries` and :func:`dataset.Dataset.temporal_boundaries`. Creating a new dataset object is straightforward but generally you will want to use an OCW data source to load the data for you.

Data Sources
------------

OCW data sources allow users to easily load :class:`dataset.Dataset` objects from a number of places. These data sources help with step 1 of an evaluation above. In general the primary file format that is supported is NetCDF. For instance, the :mod:`local`, :mod:`dap` and :mod:`esgf` data sources only support loading NetCDF files from your local machine, an OpenDAP URL, and the ESGF respectively. Some data sources, such as :mod:`rcmed`, point to externally supported data sources. In the case of the RCMED data source, the Regional Climate Model Evaluation Database is run by NASA's Jet Propulsion Laboratory. 

Adding additional data sources is quite simple. The only API limitation that we have on a data source is that it returns a valid :class:`dataset.Dataset` object. Please feel free to send patches for adding more data sources. 

A simple example using the :mod:`local` data source to load a NetCDF file from your local machine::

>>> import ocw.data_source.local as local
>>> ds = local.load_file('/tmp/some_dataset.nc', 'SomeVarInTheDataset')

Dataset Manipulations
---------------------

All :class:`dataset.Dataset` manipulations are handled by the :mod:`dataset_processor` module. In general, an evaluation will include calls to :func:`dataset_processor.subset`, :func:`dataset_processor.spatial_regrid`, and :func:`dataset_processor.temporal_rebin` to ensure that the datasets can actually be compared. :mod:`dataset_processor` functions take a :class:`dataset.Dataset` object and some various parameters and return a modified :class:`dataset.Dataset` object. The original dataset is never manipulated in the process.

Subsetting is a great way to speed up your processing and keep useless data out of your plots. Notice that we're using a :class:`dataset.Bounds` objec to represent the area of interest::

>>> import ocw.dataset_processor as dsp
>>> new_bounds = Bounds(min_lat, max_lat, min_lon, max_lon, start_time, end_time)
>>> knmi_dataset = dsp.subset(knmi_dataset, new_bounds)

Temporally re-binning a dataset is great when the time step of the data is too fine grain for the desired use. For instance, perhaps we want to see a yearly trend but we have daily data. We would need to make the following call to adjust our dataset::

>>> knmi_dataset = dsp.temporal_rebin(knmi_dataset, datetime.timedelta(days=365))

It is critically necessary for our datasets to be on the same lat/lon grid before we try to compare them. That's where spatial re-gridding comes in helpful. Here we re-grid our example dataset onto a 1-degree lat/lon grid within the range that we subsetted the dataset previously::

>>> new_lons = np.arange(min_lon, max_lon, 1)
>>> new_lats = np.arange(min_lat, max_lat, 1)
>>> knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)

Metrics
-------

Metrics are the backbone of an evaluation. You'll find a number of (hopefully) useful "default" metrics in the :mod:`metrics` module in the toolkit. In general you won't be too likely to use a metric outside of an evaluation, however you could run a metric manually if you so desired.::

>>> import ocw.metrics
>>> # Load 2 datasets
>>> bias = ocw.metrics.Bias()
>>> print bias.run(dataset1, dataset2)

While this might be exactly what you need to get the job done, it is far more likely that you'll need to run a number of metrics over a number of datasets. That's where running an evaluation comes in, but we'll get to that shortly.

There are two "types" of metrics that the toolkit supports. A unary metric acts on a single dataset and returns a result. A binary metric acts on a target and reference dataset and returns a result. This is helpful to know if you decide that the included metrics aren't sufficient. We've attempted to make adding a new metric as simple as possible. You simply create a new class that inherits from either the unary or binary base classes and override the `run` function. At this point your metric will behave exactly like the included metrics in the toolkit. Below is an example of how one of the included metrics is implemented. If you need further assistance with your own metrics be sure to email the project's mailing list!::

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

While this might look a bit scary at first, if we take out all the documentation you'll see that it's really extremely simple.::

>>> # Our new Bias metric inherits from the Binary Metric base class
>>> class Bias(BinaryMetric):
>>>     # Since our new metric is a binary metric we need to override
>>>     # the run funtion in the BinaryMetric base class.
>>>     def run(self, ref_dataset, target_dataset):
>>>         # To implement the bias metric we simply return the difference
>>>         # between the reference and target dataset's values arrays.
>>>         return ref_dataset.values - target_dataset.values

It is very important to note that you shouldn't change the datasets that are passed into the metric that you're implementing. If you do you might cause unexpected results in future parts of the evaluation. If you need to do manipulations, copy the data first and do manipulations on the copy. Leave the original dataset alone!

Handling an Evaluation
----------------------

We saw above that it is easy enough to run a metric over a few datasets manually. However, when we have a lot of datasets and/or a lot of metrics to run that can become tedious and error prone. This is where the :class:`evaluation.Evaluation` class comes in handy. It ensures that all the metrics that you choose are run over all combinations of the datasets that you input. Consider the following simple example::

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
>>> print new_eval.results
>>> print new_eval.unary_results

First we load all of our datasets and do any manipulations (which we leave out for brevity). Then we load the metrics that we want to run, namely Bias and TemporalStdDev. We then load our evaluation object.::

>>> new_eval = eval.Evaluation(ref_dataset, target_datasets, metrics)

Notice two things about this. First, we're splitting the datasets into a reference dataset (ref_dataset) and a list of target datasets (target_datasets). Second, one of the metrics that we loaded (:class:`metrics.TemporalStdDev`) is a unary metric. The reference/target dataset split is necessary to handling binary metrics. When an evaluation is run, all the binary metrics are run against every (reference, target) dataset pair. So the above evaluation could be replaced with the following calls. Of course this wouldn't handle the unary metric, but we'll get to that in a second.::

>>> result1 = bias.run(ref_dataset, target1)
>>> result2 = bias.run(ref_dataset, target2)

Unary metrics are handled slightly differently but they're still simple. Each unary metric passed into the evaluation is run against *every* dataset in the evaluation. So we could replace the above evaluation with the following calls::

>>> unary_result1 = tstd(ref_dataset)
>>> unary_result2 = tstd(target1)
>>> unary_result3 = tstd(target2)

The only other part that we need to explore to fully understand the :class:`evalution.Evaluation` class is how the results are stored internally from the run. The `results` list is a multidimensional array holding all the binary metric results and the `unary_results` is a list holding all the unary metric results. To more accurately replace the above evaluation with manual calls we would write the following::

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

Plotting can be fairly complicated business. Luckily we have `pretty good documentation <https://cwiki.apache.org/confluence/display/CLIMATE/Guide+to+Plotting+API>`_ on the project wiki that can help you out. There are also fairly simple examples in the project's example folder with the remainder of the code such as the following::

>>> # Let's grab the values returned for bias.run(ref_dataset, target1)
>>> results = bias_evaluation.results[0][0]
>>>
>>> Here's the same lat/lons we used earlier when we were re-gridding
>>> lats = new_lats
>>> lons = new_lons
>>> fname = 'My_Test_Plot'
>>>  
>>> plotter.draw_contour_map(results, lats, lons, fname)

This would give you a contour map calls `My_Test_Plot` for the requested bias metric run.
