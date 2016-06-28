Configuration File Overview
===========================

Apache Open Climate Workbench includes tools for creating and reading configuration files. Below is an explanation of the general configuration file structure, and in-depth look at the various configuration options, and explanations of how to use configuration files in an evaluation.

Getting Started
---------------

OCW configuration files are written in `YAML <http://yaml.org/>`_ with type annotations that are supported by the `PyYAML library <http://pyyaml.org/wiki/PyYAMLDocumentation>`_. Let's look at an example configuration file to get started.

.. code::

    evaluation:
        temporal_time_delta: 365
        spatial_regrid_lats: !!python/tuple [-20, 20, 1]
        spatial_regrid_lons: !!python/tuple [-20, 20, 1]

    datasets:
        reference:
            data_source: local
            file_count: 1
            path: /tmp/AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc
            variable: tasmax

        targets:
            - data_source: local
              file_count: 1
              path: /tmp/AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc
              variable: tasmax
    metrics:
        - Bias

    plots:
        - type: contour
          results_indeces:
              - !!python/tuple [0, 0]
          lats:
              range_min: -20
              range_max: 20
              range_step: 1
          lons:
              range_min: -20
              range_max: 20
              range_step: 1
          output_name: wrf_bias_compared_to_knmi
          optional_args:
              gridshape: !!python/tuple [6, 6]
    
There are 4 main categories for configuration settings: Evaluation, Datasets, Metrics, and Plots.

Evaluation Settings
-------------------

This is where you will set evaluation specific settings such as temporal and spatial bin sizes to use during dataset preparation. Visit the :doc:`Evaluation Settings <evaluation_settings>` page for additional information.

Dataset Information
-------------------

The datasets section is where you specify all the datasets to use for an evaluation. You can specify what the reference dataset should be as well as giving a list of target datasets. Visit the :doc:`Dataset Information <dataset_information>` page for additional information.

Metrics Information
-------------------

You will need to load some metrics if you want to get anything useful out of your evaluation. Visit the :doc:`Metrics Information <metrics_information>` page to learn how to specify the metrics that should be used in the evaluation.

Plots Settings
--------------

This is where you specify what plots to make after running the evaluation. The :doc:`Plots Settings <plots_settings>` page provides examples for the supported plot types.

Example Run
-----------

If you have tried the **simple_model_to_model_bias.py** example in the primary toolkit examples you can run the same evaluation but use a config file to do so instead of direct API scripting. From the **climate/ocw-config-runner/** directory run the following command to run the example::

    python ocw_evaluation_from_config.py example/simple_model_to_model_bias.yaml

.. note::

    If you haven't run the previous example which downloads the necessary datasets this evaluation will fail. The necessary local files will not have been downloaded!

Writing a Config File
---------------------

You can export an :class:`evaluation.Evaluation` object to a configuration file for easily repeatable evaluations. Checkout the documentation on the :doc:`configuration file writer API <config_writer>` for additional information.
