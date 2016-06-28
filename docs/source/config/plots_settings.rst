Plots Settings
==============

Plotting configuration information is passed in the **plots** section of the configuration file::

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

Each type of support plot has a different configuration format expected. Each of these are explained below. Note, most of these will require you to specify what result data you want included in the plots with the **results_indeces** flag. This relates the format that an Evaluation object outputs results in. Check the :class:`evaluation.Evaluation` documentation for more details.

Contour Maps
-------------

The contour maps config configures data for OCW's contour plotter :func:`plotting.draw_contour_map`::

    type: contour
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

The **lat** and **lon** parameters are specified as a range of values. Be aware that the **range_max** element is not included in the output range so you may need to adjust it slightly if you want a particular value included. The **output_name** parameter is the name of the resulting output graph. You may also pass any optional parameters that are supported by the :func:`plotting.draw_contour_map` function with the **optional_args** flag.
