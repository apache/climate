Dataset Information
===================

Dataset configuration information is passed in the **datasets** section of the configuration file. You can specify one reference dataset and one or more target datasets for your evaluation::

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
            - data_source: local
              file_count: 1
              path: /tmp/AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc
              variable: tasmax

Each **data_source** module requires datasets to be passed in a slightly different manner. Below is an explanation of the format for each of the supported data sources.

Local Dataset
-------------
.. code::

    data_source: local
    file_count: 1
    path: /tmp/AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc
    variable: tasmax

The **path** flag is the location where the dataset is located on your computer. The **variable** flag is the variable that should be pulled out of the NetCDF file once it has been opened. You pass any optional flags that are accepted by :func:`local.load_file` by using the **optional_args** flag::

    data_source: local
    file_count: 1
    path: /tmp/AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc
    variable: tasmax
    optional_args:
        elevation_index=0,
        name='foo'

.. note::

    The **file_count** flag is currently not used. It is there to support planned future functionality. However, you still need to specify it! Leave it as 1.


RCMED Dataset
-------------

.. code::
    
    data_source: rcmed
    dataset_id: 4
    parameter_id: 32
    min_lat: -10
    max_lat: 10
    min_lon: -20
    max_lon: 20
    start_time: 1997-01-01
    end_time: 2000-01-01

To load a dataset from the Jet Propulsion Laboratory's RCMED you will need to specify the above flags. The **dataset_id** and **parameter_id** are dataset specific and can be looked up on the `RCMES project website <https://rcmes.jpl.nasa.gov/content/rcmes-and-data>`_. Pretty much any common time format will be accepted for the start and end times. However, just to be safe you should try to stick with something very standard such as `ISO-8601 <http://www.w3.org/TR/NOTE-datetime>`_ formatted time values. You may also pass any optional parameters that are accepted by :func:`rcmed.parameter_dataset` with the **optional_args** flag.

ESGF Dataset
------------

In order to load an ESGF dataset you will need to specify the following parameters in addition to having an ESGF login::

    data_source: esgf
    dataset_id: obs4MIPs.CNES.AVISO.mon.v1|esg-datanode.jpl.nasa.gov
    variable: zosStderr
    esgf_password: totallynotmypassword
    esgf_username: totallynotmyusername

The **dataset_id** and **variable** flags are ESGF dataset specific. You can locate them through and ESGF nodes search page. You may also pass any optional parameters that are accepted by :func:`esgf.load_dataset` with the **optional_args** flag.


OpenDAP Dataset
---------------

A dataset can be downloaded from an OpenDAP URL with the following settings::

    data_source: dap
    url: http://test.opendap.org/dap/data/nc/sst.mnmean.nc.gz
    variable: sst

You may also pass any optional parameters that are accepted by :func:`dap.load` with the **optional_args** flag.
