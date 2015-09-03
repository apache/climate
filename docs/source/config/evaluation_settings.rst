Evaluation Settings
===================

The evaluation settings section of the configuration file allows you to set attributes that are critical for making adjustments to the loaded datasets prior to an evaluation run. Here is an example evaluation settings section of a configuration file. Below, we'll look at each of the configuration options in detail.

.. code::

    evaluation:
        temporal_time_delta: 365
        spatial_regrid_lats: !!python/tuple [-20, 20, 1]
        spatial_regrid_lons: !!python/tuple [-20, 20, 1]

Temporal Rebin
--------------

It is often necessary to temporally rebin datasets prior to an evaluation. The **temporal_time_delta** flag is where you can set the **temporal_resolution** parameter for :func:`dataset_processor.temporal_rebin`. The value that you pass here is interpreted as the number of days to assign to a :class:`datetime.timedelta` object before running the :func:`dataset_processor.temporal_rebin` function.

.. note::

    This attribute is only useful if you use the configuration data to create an :class:`evaluation.Evaluation` object with the :func:`evaluation_creation.generate_evaluation_from_config` config parser function.

Spatial Regrid
--------------

.. note::

    Some funcitonality here is still in development. Specifically, passing the spatial_regrid_* flags as lists of values.

If you need to regrid your datasets onto a new lat/lon grid you will need to set the **spatial_regrid_lats** and **spatial_regrid_lons** options. These will be passed to the :func:`dataset_processor.spatial_regrid` function along with each dataset. There are two valid ways to pass these parameters. First, you can pass them as a list of all values::

    evaluation:
        spatial_regrid_lats: [-10, -5, 0, 5, 10]
        spatial_regrid_lons: [-10, -5, 0, 5, 10]

This is generally useful if you only need to pass a few parameters or if the sequence isn't easy to define as a valid **range** in Python. The other option is to pass **range** information as a tuple. This requires you to use `PyYAML's Python Type Annotations <http://pyyaml.org/wiki/PyYAMLDocumentation#YAMLtagsandPythontypes>`_ but provides a far more compact representation::

    evaluation:
        spatial_regrid_lats: !!python/tuple [-20, 20, 1]
        spatial_regrid_lons: !!python/tuple [-20, 20, 1]

Using this style directly maps to a call to :func:`numpy.arange`::

    # spatial_regrid_lats: !!python/tuple [-20, 20, 1] becomes
    lats = numpy.arange(-20, 20, 1)

Be sure to pay special attention to the end value for your interval. The :func:`numpy.arange` function does not include the end value in the returned interval.

Subset Bounds
-------------

In order to subset the datasets down to an area of interest you will need to pass bounds information::

    evaluation:
        subset: [-10, 10, -20, 20, "1997-01-01", "2000-01-01"]

Here you're passing the bounding lat/lon box with the first 4 values as well as the valid temporal range bounds with the starting and end time values. Pretty much any common time format will be accepted. However, just to be safe you should try to stick with something very standard such as `ISO-8601 <http://www.w3.org/TR/NOTE-datetime>`_ formatted time values.
