Metrics Information
===================

.. note::

    At the moment, you can only load metrics that are in :mod:`ocw.metrics`. In the future you will also be able to specify user defined metrics here as well. However, as a work around you can define your custom metrics in the :mod:`ocw.metrics` module.

You can set the metrics you want to use in the evaluation in the **metrics** section of the config. You simply need to supply a list of the metric class names that you want to be used::

    metrics:
        - Bias
        - TemporalStdDev
