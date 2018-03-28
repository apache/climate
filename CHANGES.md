Apache Open Climate Workbench Change Log
========================================

# Release Notes - Apache Open Climate Workbench - Version 1.3.0
# Release Report - https://s.apache.org/TSNM

Sub-task

    [CLIMATE-529] - Verify that Nio dependency has been removed from mccsearch

Bug

    [CLIMATE-338] - RCMED data source loads datasets improperly based on day attribute of time values
    [CLIMATE-353] - Bounds doesn't cast input values into proper format
    [CLIMATE-374] - UI runEvaluation doesn't use $window or $location for results transition
    [CLIMATE-413] - Extend browser support for ocw-ui/frontend/config/karma.conf.js
    [CLIMATE-480] - plotter.draw_subregions requires outdated subregion object
    [CLIMATE-744] - Cannot load TRMM data from RCMED
    [CLIMATE-756] - Error: Invalid LatLng object: (NaN, NaN) when queuing APHRODITE v.1101 precipitation for the Monsoon Asia domain from RCMED
    [CLIMATE-790] - SSL errors in the esgf example
    [CLIMATE-797] - Attribute error in mask_missing_data
    [CLIMATE-826] - ValueError in model_ensemble_to_rcmed.py
    [CLIMATE-891] - Make (non-ESGF and pydap) examples script python 3 compatible
    [CLIMATE-913] - Bugs in CLI
    [CLIMATE-914] - Update dataset_processor.spatial_regrid module
    [CLIMATE-915] - Updates for the NARCCAP example configuration files
    [CLIMATE-917] - Bocumentation build error with Python3
    [CLIMATE-919] - load_dataset_from_multiple_netcdf_files() does not have default variable units
    [CLIMATE-922] - Optimize traversing in mccSearch
    [CLIMATE-929] - Incorrect indices used for temporal subset after trimming
    [CLIMATE-930] - multiple file loader forces 2D lats and lons
    [CLIMATE-931] - Documentation build error - missing module
    [CLIMATE-943] - TypeError: Cannot set property 'uiDateValidator' of undefined
    [CLIMATE-945] - Grunt Errors On Build Task
    [CLIMATE-946] - CORDEX script does not necessarily use correct interpreter when calling RCMES

Epic

    [CLIMATE-924] - Changes to RCMES and ocw for CORDEX pilot project

New Feature

    [CLIMATE-316] - Add ESGF Download Script to repository
    [CLIMATE-366] - Add 'full' temporal rebin option to UI
    [CLIMATE-426] - Create documentation for working with OCW in Eclipse
    [CLIMATE-925] - CORDEX Config File Template
    [CLIMATE-926] - Metadata Extractors
    [CLIMATE-927] - RCMES script for running multiple evaluations

Improvement

    [CLIMATE-230] - Line colors in time series cycles through too few colors
    [CLIMATE-348] - Add better default naming for local files
    [CLIMATE-388] - Make UI backend 'parameters' endpoint more RESTful
    [CLIMATE-465] - Add class level documentation to all OCW python examples
    [CLIMATE-625] - Update draw_histogram and draw_marker_on_map documentation
    [CLIMATE-626] - Update doc strings in Downscaling class
    [CLIMATE-863] - Address warning, deprecation, etc. within Travis-CI log output
    [CLIMATE-887] - test_get_netcdf_variable_names setUp to run only once for the test case
    [CLIMATE-912] - Upgrade mccSearch code from Python2 > 3
    [CLIMATE-920] - Make examples Python 3 compatible
    [CLIMATE-928] - temporal_subset should trim edges of dataset times to ensure months divide evenly into years
    [CLIMATE-938] - Unify format of the time information from a netCDF file

Task

    [CLIMATE-631] - Add documentation on ESGF credential issues
    [CLIMATE-762] - Automate symlinking ocw-vm frontend to backend to allow for serving of files with bottle.
    [CLIMATE-881] - Add podaacpy to ocw-conda-dependencies.txt

# Release Notes - Apache Open Climate Workbench - Version 1.2.0
# Release Report - https://s.apache.org/120release

Sub-task

    [CLIMATE-880] - Delete conda_recipes directory

Bug

    [CLIMATE-798] - Redundant code in evaluations.py
    [CLIMATE-835] - Fix documentation warnings
    [CLIMATE-842] - Add shape files to package installation
    [CLIMATE-844] - Attribute Error in test_smoke.py
    [CLIMATE-846] - ESGF loader fails with new changes to run_RCMES.py
    [CLIMATE-852] - [OCW Documentation] Theme not found error
    [CLIMATE-853] - Broken documentation in dap.py
    [CLIMATE-855] - Fix test_local and test_dataset_processor
    [CLIMATE-857] - Using SonarQube.com with Travis CI
    [CLIMATE-858] - Fix Travis Build
    [CLIMATE-862] - More updates to conda recipe files
    [CLIMATE-864] - Disable podaac until dataset_loader and data_source are fixed
    [CLIMATE-882] - local data source is not Python 3 compatible
    [CLIMATE-883] - Ensure python 3 builds pass unit tests
    [CLIMATE-884] - Cannot run grunt serve in frontend of ocw gui
    [CLIMATE-886] - Upgrade Frontend Dependencies
    [CLIMATE-889] - Fix Travis Build
    [CLIMATE-892] - Fix GPM IMERG data loader
    [CLIMATE-893] - Debugging wet_spell_analysis
    [CLIMATE-894] - Debugging regrid_spatial_mask
    [CLIMATE-895] - Make plotter compatible with matplotlib 2.0
    [CLIMATE-897] - Make sure shapes of numpy arrays contain only integer values
    [CLIMATE-899] - Update the GPM loader
    [CLIMATE-906] - Fix tests in master (podaacpy integration)
    [CLIMATE-910] - Throw an exception for inconsistent temporal reshaping / rebinning operatations

Improvement

    [CLIMATE-486] - Normalize DSP function parameter ordering
    [CLIMATE-488] - Change Dataset.time_range to Dataset.temporal_boundaries
    [CLIMATE-825] - Coalesce data sources into one module
    [CLIMATE-827] - Adding spatial masking options
    [CLIMATE-832] - Add smoke tests
    [CLIMATE-833] - Update travis.yml to use smoke tests
    [CLIMATE-838] - Update configuration files and example scripts to use new DatasetLoader
    [CLIMATE-839] - Further improvements to DatasetLoader
    [CLIMATE-841] - ocw.dataset_processor.subset
    [CLIMATE-847] - Support multiple observation / reference datasets in run_RCMES.py
    [CLIMATE-848] - Support CORDEX boundary options in RCMES
    [CLIMATE-851] - Have nosetests log to STDOUT
    [CLIMATE-854] - Ensure that ocw runs with Python 3.X
    [CLIMATE-859] - Enable restructured text markdown for Pypi uploads
    [CLIMATE-865] - Update dataset_name argument in local.load_multiple_files
    [CLIMATE-873] - easy-ocw install-ubun.sh should use miniconda3
    [CLIMATE-874] - Remove Easy-OCW
    [CLIMATE-875] - Upgrade to Podaacpy 1.4.0
    [CLIMATE-879] - Move OCW recipes to conda-forge
    [CLIMATE-885] - Upgrade to Podaacpy 1.9.0
    [CLIMATE-907] - Fix VisibleDeprecationWarning's in ocw.tests.test_dataset_processor.TestTemporalSubset
    [CLIMATE-909] - An example script to evaluate joint PDF of precipitation intensity and duration

New Feature

    [CLIMATE-769] - Create data source input for NASA JPL PO.DAAC
    [CLIMATE-784] - Smoke Tests and Continuous Integration Infrastructure
    [CLIMATE-861] - An example to plot aerosol optical depth climatology from NASA MISR instrument
    [CLIMATE-903] - Adding a module to calculate the least square trend and standard error
    [CLIMATE-905] - Box whisker plot to evaluate simulate trends

Task

    [CLIMATE-763] - Include instructions in webapp documentation on how to use yo
    [CLIMATE-866] - Create ocw conda package against Python3.x as well as Python 2.7
    [CLIMATE-868] - Move podaacpy conda recipie to official podaacpy repository
    [CLIMATE-878] - Add LICENSE file to MANIFEST.in
    [CLIMATE-896] - Patch code updates for matplotlib 2.0 compatibility in 1.1.0 conda recipe

# Release Notes - Apache Open Climate Workbench - Version 1.1.0
# Release Report - https://s.apache.org/110report

Sub-task

    [CLIMATE-709] - Drop Freetype from conda environment file
    [CLIMATE-712] - Update VM init script
    [CLIMATE-713] - Update VM wiki page with new instructions
    [CLIMATE-757] - Fix ERROR: test suite for <class 'ocw.tests.test_dap.TestDap'>
    [CLIMATE-758] - Fix failing tests in test_local.py
    [CLIMATE-759] - Fix failing tests in test_dataset_processor.py
    [CLIMATE-795] - Add tests for dataset_processor module
    [CLIMATE-801] - Add tests for dataset module
    [CLIMATE-802] - Add tests for evaluation module
    [CLIMATE-805] - Add tests for utils module
    [CLIMATE-806] - Add tests for local module
    [CLIMATE-808] - Add tests for plotter module
    [CLIMATE-812] - Fix PEP8 Violations in dataset processor
    [CLIMATE-813] - Fix PEP8 Violations in utils
    [CLIMATE-814] - Fix PEP8 Violations in dataset

Bug

    [CLIMATE-407] - Dataset select can queue empty RCMED datasets
    [CLIMATE-517] - Start and End day values overlap in dataset display
    [CLIMATE-556] - easy_install scripts should create a new virtualenv e.g. -e flag, by default
    [CLIMATE-557] - Investigate dubious GEOS installation output
    [CLIMATE-560] - Incorrect assumption for installation directory within easy-ocw/install-osx.sh
    [CLIMATE-561] - easy-ocw/install-osx.sh script should not assume relative locations for dependency utilitiy files
    [CLIMATE-562] - Make nightly documentation SNAPSHOT's available for public consumption
    [CLIMATE-616] - missing dependencies
    [CLIMATE-634] - fix calc_climatology_monthly
    [CLIMATE-642] - Improper unit set in water_flux_unit_conversion
    [CLIMATE-668] - ocw.dataset_spatial_resolution needs to be fixed
    [CLIMATE-669] - OCW spatial_boundary bug
    [CLIMATE-671] - Inappropriate spatial subset for datasets on curvilinear grids
    [CLIMATE-698] - Handling missing values in ocw.dataset_processor.temporal_rebin_with_time_index
    [CLIMATE-707] - Rework Easy OCW scripts to only use conda
    [CLIMATE-710] - OCW Package Tests are Broken
    [CLIMATE-711] - conda-install won't source .bashrc properly
    [CLIMATE-716] - Dataset object manipulation when plotting a Taylor diagram using a configuration file
    [CLIMATE-718] - Temporal slice of two-dimensional model output
    [CLIMATE-719] - Subsetting model data on curvillinear grids in the configuration file runner
    [CLIMATE-722] - Extrapolation issues in spatial_regrid
    [CLIMATE-724] - Debugging load_dataset_from_multiple_netcdf_files
    [CLIMATE-725] - Ensure that OCW 1.1 Test PyPi Works as Expected
    [CLIMATE-737] - Debugging dataset_processor.temporal_rebin
    [CLIMATE-738] - Google jsapi Uses HTTP Rather Than HTTPS
    [CLIMATE-739] - main.html refers to missing img/globe.png image
    [CLIMATE-740] - Add img Path Handler To run_webservices.py
    [CLIMATE-742] - ocw.data_source.local.py cannot properly detect the altitude dimension
    [CLIMATE-743] - Update utils.normalize_lat_lon_values
    [CLIMATE-745] - Report an Issue Link and @copyright year are incorrect in ocw-ui
    [CLIMATE-748] - Debugging ocw.dataset_processor
    [CLIMATE-749] - Changing temporal_resolution key in CLI
    [CLIMATE-750] - $scope.fileLoadFailed Compares On Boolean Rather Than String
    [CLIMATE-752] - Converting the unit of CRU cloud fraction by adding an option to configuration files
    [CLIMATE-761] - Error in easy-ocw install-ubuntu Basemap stage
    [CLIMATE-764] - Screen size of CLI
    [CLIMATE-771] - Critical bugs in LAT_NAMES and LON_NAMES in local.py
    [CLIMATE-781] - Fix the ESGF example in run_RCMES.py
    [CLIMATE-786] - Update rcmed.py and test_rcmed.py
    [CLIMATE-799] - TypeError in subset function
    [CLIMATE-800] - TypeError in _rcmes_calc_average_on_new_time_unit
    [CLIMATE-804] - normalize_lat_lon_values does not work
    [CLIMATE-807] - Add test coverage badge to README
    [CLIMATE-809] - Fix coveragerc file
    [CLIMATE-818] - local.load_dataset_from_multiple_netcdf_files() does not accept user entered lon_name and lat_name fields.
    [CLIMATE-822] - ValueError in RCMES test

Improvement

    [CLIMATE-379] - Allow dataset name customization in UI
    [CLIMATE-409] - Implement a language sensitive map (I18n) for WebApp
    [CLIMATE-421] - Add a download page for OCW
    [CLIMATE-539] - Get OCW on to PyPI
    [CLIMATE-569] - Updating rcmes.py using the latest OCW library
    [CLIMATE-572] - Address deprecation and WARN's in ocw-ui/frontend npm install
    [CLIMATE-573] - Remove sudo requirement to install virtualenv within install-ubuntu.sh
    [CLIMATE-617] - Documentation Audit
    [CLIMATE-632] - Adding a loader to handle multiple MERRA reanalysis HDF files stored on a local disk
    [CLIMATE-635] - Add documentation to dev guide regarding test running
    [CLIMATE-652] - Calculation of area weighted spatial average
    [CLIMATE-653] - Netcdf file generator with subregion information
    [CLIMATE-657] - Adding functions to calculate metrics
    [CLIMATE-658] - Restructure evaluation results
    [CLIMATE-666] - Replace examples with the RCMES script and yaml files
    [CLIMATE-672] - Update the input validation function for OCW datasets
    [CLIMATE-673] - Update the module to load multiple netcdf files
    [CLIMATE-674] - Update the spatial_regrid module to handle data on curvilinear grids or irregularly spaced grids
    [CLIMATE-676] - Cleaning up the examples
    [CLIMATE-678] - Provide link to Python API documentation
    [CLIMATE-680] - A new loader to read WRF precipitation data with a file list
    [CLIMATE-681] - Update the loader to read WRF data (other than precipitation)
    [CLIMATE-684] - Update README with Python API docs
    [CLIMATE-700] - Complete examples to reproduce a RCMES-based paper
    [CLIMATE-701] - Examples for evaluation of CORDEX-Arctic RCMs
    [CLIMATE-702] - Print Jenkins test result to Github issue
    [CLIMATE-703] - Remove pop-up windows from metrics_and_plots.py
    [CLIMATE-704] - Sensitivity of spatial boundary check in dataset_processor
    [CLIMATE-708] - Switch VM build over to conda environment approach
    [CLIMATE-714] - Updating the regridding routine
    [CLIMATE-720] - Revise file structure
    [CLIMATE-723] - Update subset module for regional climate model output
    [CLIMATE-726] - Update configuration files
    [CLIMATE-727] - Ensure that ocwui package.json version is updated in line with releases
    [CLIMATE-728] - Address WARN's when building ocwui
    [CLIMATE-729] - Remove config file from NARCCAP examples
    [CLIMATE-730] - Add OCW logo to ocw-ui header navigation panel
    [CLIMATE-731] - Update ocw.dataset_processor.temperature_unit_conversion
    [CLIMATE-734] - Adjust size of the color bars in the map plot of biases
    [CLIMATE-735] - Update utils.decode_time_values
    [CLIMATE-736] - Update dataset_processor.write_netcdf_multiple_datasets_with_subregions
    [CLIMATE-741] - Adding configuration files to evaluate CORDEX-Africa regional climate models
    [CLIMATE-754] - RCMED dataset parameters need to be more verbose
    [CLIMATE-760] - Address documentation warnings
    [CLIMATE-766] - Easy-ocw/install-ubuntu.sh script is broken
    [CLIMATE-770] - Make boundary checking optional in spatial_regrid
    [CLIMATE-777] - cli_app shows a list of model
    [CLIMATE-778] - Cosmetic updates for the cli_app
    [CLIMATE-779] - Add ESGF Integration into run_RCMES.py
    [CLIMATE-780] - Add Travis-CI build status to README.md
    [CLIMATE-783] - Update ESGF examples
    [CLIMATE-811] - Add landscape.io integration
    [CLIMATE-815] - Fix all PEP8 Violations in ocw module
    [CLIMATE-816] - Add requires.io badge to README.md
    [CLIMATE-817] - More informative error messages for data_source.load_file()
    [CLIMATE-820] - Update pip requirements
    [CLIMATE-821] - write_netcdf() assumes lat and lon are 1D arrays

New Feature

    [CLIMATE-246] - Develop PoweredBy Logo for OCW
    [CLIMATE-367] - Add more 'new contributor' information
    [CLIMATE-677] - Homebrew Formula for OCW
    [CLIMATE-683] - A new loader to read multiple netCDF files with a file list and spatial mask
    [CLIMATE-687] - A new loader to read GPM precipitation data with a file list
    [CLIMATE-692] - A new loader to read NLDAS data with a file list
    [CLIMATE-694] - A new module to rebin a dataset using time index
    [CLIMATE-696] - Examples to evaluate CORDEX-ARCTIC RCMs
    [CLIMATE-715] - Adding a new demo tab along with the evaluate and result so that user can see the demo of the ocw in this tab.
    [CLIMATE-732] - Update dataset_processor.temporal_rebin
    [CLIMATE-733] - Update run_RCMES.py
    [CLIMATE-747] - Adding configuration files as an example of NASA's downscaling project
    [CLIMATE-829] - Add conda package recipes

Story

    [CLIMATE-418] - Remove hard links to mailing lists

Task

    [CLIMATE-611] - SSL certificate verify error
    [CLIMATE-659] - Remove SpatialMeanOfTemporalMeanBias
    [CLIMATE-695] - Adding h5py library
    [CLIMATE-782] - Resolve BeautifulSoup warnings in esgf data_source and add myproxyclient to easy-ocw install
    [CLIMATE-831] - Add License Headers to conda recipes

Test

    [CLIMATE-679] - Statistical downscaling examples

Wish

    [CLIMATE-690] - Data Sources Class for NSIDC's Arctic Data Explorer Platform
    [CLIMATE-691] - Provide link to RCMED Query Service Documentation from within RCMED data source Python docs

Release Notes - Apache Open Climate Workbench - Version 1.0.0

** Sub-task
    * [CLIMATE-578] - Update release docs to include documentation version bumps
    * [CLIMATE-585] - change the bias calculations in the metrics class
    * [CLIMATE-586] - add barchart as a plotter option
    * [CLIMATE-587] - Unit conversion

** Bug
    * [CLIMATE-566] - Output redirects in Easy-OCW clobber install log
    * [CLIMATE-571] - Easy-OCW checks for installed applications can fail
    * [CLIMATE-595] - Dateutil package is not included in pip install requirements
    * [CLIMATE-596] - Dataset variables are not propagated correctly through dataset_processor functions
    * [CLIMATE-605] - Typo in plotter.draw_contour_map docstring
    * [CLIMATE-607] - Config Parser tests are breaking
    * [CLIMATE-618] - VM Build is using an old easy-ocw install script reference
    * [CLIMATE-619] - Ubuntu easy-ocw install script issues in quiet mode
    * [CLIMATE-636] - Bounds __str__ function doesn't return correct data format
    * [CLIMATE-638] - Subregion_portrait example doesn't run
    * [CLIMATE-640] - Time series with subregions example doesn't run
    * [CLIMATE-641] - missing data handling in OCW metrics
    * [CLIMATE-650] - Fix the ensemble calculation

** Improvement
    * [CLIMATE-467] - Handling various calendar types
    * [CLIMATE-508] - Adding statistical downscaling capability
    * [CLIMATE-563] - Add ESGF module to documentation 
    * [CLIMATE-577] - Bump docs version up to 1.0.0
    * [CLIMATE-580] - Config Based Evaluation Improvements
    * [CLIMATE-581] - Export an evaluation to a config file
    * [CLIMATE-582] - Add config based evaluation documentation to sphinx docs
    * [CLIMATE-583] - Add better plot support to config based evaluations
    * [CLIMATE-588] - Refactor config based evaluation layout
    * [CLIMATE-594] - Add Dataset location tracking to data sources
    * [CLIMATE-599] - Add example config based evaluation run to sphinx docs
    * [CLIMATE-600] - Add a pylint RC file for code linting
    * [CLIMATE-602] - Add support for multiple plot indices to config based contour map generation
    * [CLIMATE-603] - Move simple_model_to_model_bias *.nc download to /tmp
    * [CLIMATE-606] - Spell "indices" properly in the config parser
    * [CLIMATE-608] - Add mailmap file to repo
    * [CLIMATE-609] - Add source flag to dataset origin information
    * [CLIMATE-621] - Make ESGF data source save folder configurable
    * [CLIMATE-633] - Adding a loader to handle WRF output stored on a local disk
    * [CLIMATE-637] - Subregion Clean up and Improvements
    * [CLIMATE-639] - Add subregion support to config runner
    * [CLIMATE-648] - Propagation of missing data information from each dataset
    * [CLIMATE-651] - A new module to calculate area mean and standard deviation with given subregion information

** Task
    * [CLIMATE-567] - Update DOAP for 0.5
    * [CLIMATE-574] - Remove .DS_Store from repo
    * [CLIMATE-575] - Implement initial config based execution of an evaluation
    * [CLIMATE-593] - Add ASF headers to config parser

** Wish
    * [CLIMATE-30] - Apache Open Climate Workbench Logo 


Release Notes - Apache Open Climate Workbench - Version 0.5

** Sub-task
    * [CLIMATE-43] - Update evaluation running code to use new re-grid options
    * [CLIMATE-44] - Update backend with ability to handle user-specified re-grid calls.
    * [CLIMATE-341] - Refactor "calcAnnualCycleMeans" metric from metrics_kyo.py
    * [CLIMATE-497] - Update OCW release management process documentation
    * [CLIMATE-519] - Fix ESGF directory structuring
    * [CLIMATE-520] - Add ESGF wrapper to setup.py
    * [CLIMATE-540] - Port 'calcBiasAveragedOverTimeAndDomain' method over to ocw/metrics.py module
    * [CLIMATE-541] - Port 'calcRootMeanSquareDifferenceAveragedOverTimeAndDomain' method over to ocw/metrics.py module
    * [CLIMATE-542] - Port 'calcTemporalCorrelation' method over to ocw/metrics.py module
    * [CLIMATE-543] - Port 'calcNashSutcliff' method over to ocw/metrics.py module
    * [CLIMATE-544] - Port 'calc_temporal_anom_cor' method to ocw/metrics.py
    * [CLIMATE-545] - Port 'calc_spatial_anom_cor' method over to ocw/metrics.py module
    * [CLIMATE-546] - Refactor 'calcPdf' method from metrics_kyo.py
    * [CLIMATE-549] - Minor updates to the SpatialMeanOfTemporalMeanBias and RMSError metrics

** Bug
    * [CLIMATE-487] - data_source.local returns bad error when incorrect file path is provided
    * [CLIMATE-530] - Include license acknowledgment for all mccsearch dependencies
    * [CLIMATE-548] - Vagrant references should not exist in easy-ocw ubuntu script
    * [CLIMATE-554] - Changed metric names break Sphinx build

** Improvement
    * [CLIMATE-265] -  Model Ensemble to RCMED Evaluation
    * [CLIMATE-340] - Transfer metrics from the original codebase over to ocw/metrics.py
    * [CLIMATE-371] - local.load_file should accept lat/lon/time variable names
    * [CLIMATE-372] - Data_sources should allow dataset naming
    * [CLIMATE-496] - Address discrepancies within 0.4 RC#1
    * [CLIMATE-533] - Revisit mccsearch README making updates as required
    * [CLIMATE-552] - Cleanup local.py data source
    * [CLIMATE-558] - Add better links to external documentation

** New Feature
    * [CLIMATE-38] - Add regrid options
    * [CLIMATE-39] - Add ability for user to select spatial re-grid options
    * [CLIMATE-523] - Integrate mccsearch module into master branch
    * [CLIMATE-538] - Allow selection of elevation level on dataset load

** Task
    * [CLIMATE-373] - Publish documentation build to Read The Docs
    * [CLIMATE-411] - Create Pyhton lib documentation
    * [CLIMATE-518] - Add ESGF data source
    * [CLIMATE-534] - Make sure everyone on OCW PMC has PMC permissions in Jira
    * [CLIMATE-535] - Update mccsearch files.py to use current replacement of toolkit.process function
    * [CLIMATE-536] - Update mccsearch files.py to use current replacement of utils.fortran function
    * [CLIMATE-537] - Update mccsearch files.py to use current replacement of utils.misc function
    * [CLIMATE-550] - Drop bottlemet.py from OCW UI Backend
    * [CLIMATE-551] - Drop old RCMET toolkit from code base
    * [CLIMATE-553] - Add an example for the ESGF datasource
    * [CLIMATE-555] - Update Sphinx documentation version number



Release Notes - Apache Open Climate Workbench - Version 0.4

** Sub-task
    * [CLIMATE-271] - Breaking down "run_rcmes_processing.py" code to more functions
    * [CLIMATE-328] - Add Helpers for converting NetCDF time data to Python datetimes
    * [CLIMATE-329] - Add tests for ocw.utils
    * [CLIMATE-330] - Remove datetime conversion code from ocw.data_sources.local
    * [CLIMATE-332] - Rewrite UI evaluation code with OCW
    * [CLIMATE-333] - Integrate OCW-UI with refactored backend
    * [CLIMATE-334] - Drop old OCW-UI front/back end code
    * [CLIMATE-335] - Add OCW-UI to documentation build
    * [CLIMATE-361] - Normalize datetime values in UI backend
    * [CLIMATE-394] - Remove inactive subregion file box
    * [CLIMATE-482] - Add non-rebinning version of StdDevRatio
    * [CLIMATE-483] - Add non-rebinning version of PatternCorrelation metric
    * [CLIMATE-497] - Update OCW release management process documentation
    * [CLIMATE-498] - Update OCW DOAP.rdf to accommodate recent releases
    * [CLIMATE-499] - Add directions to build documentation to README
    * [CLIMATE-500] - Determine actions and address DRAT reporting output.
    * [CLIMATE-502] - Transition frontend tests to new frontend
    * [CLIMATE-506] - Find temporal overlap between models and obervations
    * [CLIMATE-510] - Find spatial overlap between models and observations
    * [CLIMATE-511] - OCW cli should let user to pick target and reference dataset before run the evaluation
    * [CLIMATE-512] - Replace frontend-ui code with new Yeoman/Grunt/Bower powered frontend
    * [CLIMATE-513] - Document new UI features on Wiki



** Bug
    * [CLIMATE-49] - Add the 'obs' regrid option into toolkit.do_data_prep.prep_data function
    * [CLIMATE-298] - Remove external dependencies from test_local
    * [CLIMATE-320] - To make UI handle CMIP5 model outputs
    * [CLIMATE-321] - dataset_processor._get_subregion_slice_indices cannot handle imprecise subregion input
    * [CLIMATE-322] - dataset_processor._get_subregion_slice_indices cannot handle imprecise start and end time input
    * [CLIMATE-339] - Metrics.py has typo in Class TemporalStdDev, def Run (axi --> axis) + test_metrics.py need to be modified
    * [CLIMATE-344] - Temporal rebin doesn't propagate dataset name or variable name
    * [CLIMATE-345] - Spatial regrid doesn't propagate dataset name or variable name
    * [CLIMATE-346] - Subsetting must be performed after Temporal Rebin
    * [CLIMATE-350] - Access-Control-Allow-Origin is not set on response from UI backend
    * [CLIMATE-352] - Dataset.spatial_boundaries doesn't return proper data format
    * [CLIMATE-354] - ResultCtrl doesn't handle missing cache directory removal properly
    * [CLIMATE-363] - Backend processing doesn't parse temporal resolution properly
    * [CLIMATE-364] - Invalid metric names doesn't exclude ABCMeta
    * [CLIMATE-380] - Unary metric evaluation fails on reference dataset
    * [CLIMATE-382] - UI backend return types aren't recognized as JSON
    * [CLIMATE-387] - reStructuredText is malformed in UI backend
    * [CLIMATE-390] - OCW UI maps no longer display properly
    * [CLIMATE-391] - Date ranges for UI evaluation are not normalized
    * [CLIMATE-392] - OCW Dataset should shift lon values that range from 0-360
    * [CLIMATE-396] - RCMED Parameters are improperly parsed in UI backend
    * [CLIMATE-398] - OCW is unable to parse an acceptable date format
    * [CLIMATE-402] - Dataset bounds are not properly set in ParameterSelectCtrl
    * [CLIMATE-405] - UI backend documentation isn't building for /parameters/bounds
    * [CLIMATE-412] - Create README for OCW
    * [CLIMATE-414] - Overhaul OCW Wiki
    * [CLIMATE-416] - Clean up UI backend tests
    * [CLIMATE-420] - Download link to most recent release is broken
    * [CLIMATE-422] - easy-ocw install.sh still references svn code
    * [CLIMATE-423] - Evaluation Unary Metric is missing return resutls
    * [CLIMATE-435] - Fix easy-ocw path in VM build
    * [CLIMATE-437] - Remove provisioning from Vagrant VM build
    * [CLIMATE-440] - Remove local PATH_LEADER settings from test_directory_helpers
    * [CLIMATE-442] - Cannot have multiple nested directories that don't exist in UI backend tests
    * [CLIMATE-445] - Remove unneeded OCW checkout from easy-ocw Ubuntu script
    * [CLIMATE-449] - NetCDF4 is installed twice in easy-ocw Ubuntu install
    * [CLIMATE-451] - Getting Errors in virtualenv wrapper after running easy-ocw/install-osx.sh 
    * [CLIMATE-454] - VM Build does not copy dependency files to install directory
    * [CLIMATE-455] - utils.reshape_monthly_to_annually should modify a copy of the passed dataset
    * [CLIMATE-470] - utils.parse_time_base fails to handle time format
    * [CLIMATE-472] - Contour map colorbar labels overlap with large float values
    * [CLIMATE-481] - StddevRatio and PatternCorr metrics outputting bad values
    * [CLIMATE-503] - OCW-cli notification center is broken due to passing wrong argument
    * [CLIMATE-504] - OCW cli cannot get observation spatial resolution 
    * [CLIMATE-514] - Dependencies are missing from package.json
    * [CLIMATE-516] - Backend static file serving does not work
    * [CLIMATE-517] - Start and End day values overlap in dataset display


** Documentation
    * [CLIMATE-54] - Updating the docstrings in metrics.py


** Improvement
    * [CLIMATE-47] - precipFlag attribute within the Model class needs to be refactored
    * [CLIMATE-91] - Webapps directory restructure
    * [CLIMATE-241] - Make old docstrings in plotter.py sphinx compliant
    * [CLIMATE-261] - Consolidate Code that converts a String into a Datetime Object
    * [CLIMATE-262] - Develop simple examples of an End to End Evaluation using OCW API
    * [CLIMATE-270] - UI Back-End update 
    * [CLIMATE-309] - Add OpenDAP support to OCW
    * [CLIMATE-310] - Update setup.py version
    * [CLIMATE-311] - Add Sphinx doc building
    * [CLIMATE-312] - Add dataset.py to Sphinx build
    * [CLIMATE-313] - Add dataset_processor.py to Sphinx build
    * [CLIMATE-314] - Add evaluation.py to Sphinx build
    * [CLIMATE-315] - Add metrics.py to Sphinx build
    * [CLIMATE-317] - Fix plotter.py documentation
    * [CLIMATE-318] - Add plotter.py to the Sphinx build
    * [CLIMATE-319] - Add data sources to Sphinx build
    * [CLIMATE-324] - Reorganize OCW UI Code
    * [CLIMATE-325] - Reorganize OCW UI Backend Code
    * [CLIMATE-326] - Refactor OCW-UI backend services
    * [CLIMATE-331] - Make OCW-UI use OCW code instead of old RCMES backend
    * [CLIMATE-343] - Integrate utils.taylor into OCW
    * [CLIMATE-347] - UI backend grid shape calculations can result in widely imbalanced shapes
    * [CLIMATE-349] - Refactoring "reshapeMonthlyData" from rcmes/utils/misc.py 
    * [CLIMATE-351] - obs4MIPs data ingestion
    * [CLIMATE-358] - Truncate lat/lon values in DatasetDisplayCtrl
    * [CLIMATE-359] - Change wording of reference dataset selection to reflect new backend
    * [CLIMATE-360] - Fix subsetting in UI backend
    * [CLIMATE-370] - Update Easy-OCW
    * [CLIMATE-377] - Update UI to latest Angular version
    * [CLIMATE-378] - Setup proper build/dependency management for UI
    * [CLIMATE-395] - Add more unit tests for normalize_lat_lon_values() helper
    * [CLIMATE-397] - Switch UI backend over to safe_subset
    * [CLIMATE-399] - Use functions in numpy.testing for unit tests involving array comparisons
    * [CLIMATE-401] - Remove UnaryMetrics from UI settings menu
    * [CLIMATE-403] - Integrate /parameters/bounds endpoint into UI frontend
    * [CLIMATE-408] - Dataset select window should have a close button
    * [CLIMATE-427] - Make easy-ocw pip dependencies install from a requirements file
    * [CLIMATE-428] - Add versions to all the easy-ocw dependency installs
    * [CLIMATE-429] - Add sphinx doc building dependencies to easy-ocw
    * [CLIMATE-430] - Add link to relevant wiki documentation from easy-ocw install scripts
    * [CLIMATE-432] - Add wiki page for easy-ocw
    * [CLIMATE-433] - Add wiki page for Vagrant VM build
    * [CLIMATE-434] - Add README for Github
    * [CLIMATE-436] - Pull VM OCW code from ASF repo
    * [CLIMATE-438] - adding new time format to data_source/local.py
    * [CLIMATE-439] - Refactoring 'calcClimYear' function to OCW API
    * [CLIMATE-441] - easy-ocw needs to check if a previous 'ocw' virtualenv exists
    * [CLIMATE-443] - move calcSpatialStdevRatio to OCW metrics
    * [CLIMATE-444] - move calcPatternCorrelation to OCW metrics
    * [CLIMATE-446] - easy-ocw Anaconda download should point to an archive link
    * [CLIMATE-447] - ocw.tests lacks __init__.py
    * [CLIMATE-450] - OCW examples download remote netCDF files without checking if they exist
    * [CLIMATE-452] - Add Ubuntu Unity desktop install option to OCW VM build
    * [CLIMATE-453] - Add Taylor Diagram example
    * [CLIMATE-456] - Update DAP tests to use setupClass method for initialization
    * [CLIMATE-457] - Clean up after Easy-OCW install on Ubuntu
    * [CLIMATE-458] - Add OCW UI setup to VM build
    * [CLIMATE-462] - Move Ubuntu Easy OCW install leftovers cleanup into VM build
    * [CLIMATE-464] - Move calcClimSeason to utils
    * [CLIMATE-468] - Add helpful links to the OCW-VM build
    * [CLIMATE-471] - Add seasonal versions of SpatialStdDevRatio and SeasonalPatternCorrelation
    * [CLIMATE-473] - Add a gitignore
    * [CLIMATE-474] - Make colorbar labels not use scientific notation
    * [CLIMATE-475] - Make metric imports in ocw.tests not explicit
    * [CLIMATE-476] - OCW objects should implement __str__
    * [CLIMATE-477] - Add nose-exclude as a development dependency
    * [CLIMATE-479] - Clean up return type documentation in toolkit
    * [CLIMATE-489] - Improve dataset_processor.subset()'s ValueError Message
    * [CLIMATE-492] - Move OCW-UI over to Yeomann, Bower, and Grunt
    * [CLIMATE-496] - Address discrepancies within 0.4 RC#1

** New Feature
    * [CLIMATE-137] - OCW refactoring code
    * [CLIMATE-327] - Add OCW Utils module
    * [CLIMATE-336] - test (Unit Test) for Class BIAS on metrics.py
    * [CLIMATE-337] - test (Unit Test) for Class TemporalStdDev on metrics.py
    * [CLIMATE-386] - Add NetCDF writer to Dataset Processor
    * [CLIMATE-393] - Add less strict subsetting functionality
    * [CLIMATE-404] - OCW Command Line Tool
    * [CLIMATE-425] - Example of Temporal STD Metric with Contour Map plot
    * [CLIMATE-463] - refactoring calcBiasAveragedOverTime metric
    * [CLIMATE-505] - OCW cli to support multi observations and multi models

** Task
    * [CLIMATE-2] - Refactor source code to use ASF package names
    * [CLIMATE-127] - Easy-RCMET changes after transition
    * [CLIMATE-171] - Preparing daily TRMM data to evaluate NARCCAP models
    * [CLIMATE-259] - Create branch to refactor updates to ui/services to support multiple metrics/plotting
    * [CLIMATE-342] - utils.taylor lacks proper licensing
    * [CLIMATE-355] - Update UI frontend tests
    * [CLIMATE-356] - Pull metric names from backend for UI dropdowns
    * [CLIMATE-357] - ParameterSelectCtrl should only allow users to select values on a integer grid
    * [CLIMATE-368] - Add JIRA labels for issue difficulty estimation
    * [CLIMATE-369] - Setup automatic VM build
    * [CLIMATE-381] - Update setup.py to reflect the change from Incubating to Top Level Project
    * [CLIMATE-384] - Clean new git repo's pack file
    * [CLIMATE-385] - Copyright dates need updated
    * [CLIMATE-415] - Create a *Contributing to OCW* wiki page 
    * [CLIMATE-417] - Backend UI tests are missing ASF Header
    * [CLIMATE-431] - Add ASF header to easy-ocw install scripts
    * [CLIMATE-460] - Drop old RCMET Webapp
    * [CLIMATE-461] - Drop old RCMET VM
    * [CLIMATE-469] - Add ASF headers to OCW example files
    * [CLIMATE-484] - Remove rebinning metrics
    * [CLIMATE-485] - Ensure all metrics are included in Sphinx build
    * [CLIMATE-490] - Drop DISCLAIMER.txt
    * [CLIMATE-491] - Add author note to TaylorDiagram


Release Notes - Apache Open Climate Workbench - Version 0.3-incubating

** Sub-task
    * [CLIMATE-190] - test_local.py
    * [CLIMATE-227] - OCW rcmed.py code
    * [CLIMATE-228] - test_rcmed.py
    * [CLIMATE-235] - Migrate Temporal Binning Functionality to dataset_processor module
    * [CLIMATE-236] - Add Dataset Ensemble Support to the ocw.dataset_processor module
    * [CLIMATE-237] - Add Subset Generation function to dataset_processor module
    * [CLIMATE-263] - Create local netCDF to local netCDF Evaluation Example using OCW Core API
    * [CLIMATE-264] - Local NetCDF File to RCMED Evaluation (temporal and spatial regridding of data)
    * [CLIMATE-266] - local.py and associated tests import code one level below the ocw folder
    * [CLIMATE-268] - local.py returns a Dataset Object with a 4-D Array for the Dataset.values
    * [CLIMATE-280] - Add OnBlur directive tests
    * [CLIMATE-281] - Evaluation Class methods need 'self' added to them
    * [CLIMATE-285] - Create UnaryMetric base class
    * [CLIMATE-286] - Create BinaryMetric base class
    * [CLIMATE-287] - Remove Metric Base Class
    * [CLIMATE-289] - Update Bias to use BinaryMetric
    * [CLIMATE-290] - Update TemporalStdDev to use UnaryMetric
    * [CLIMATE-291] - Update Metric handling in Evaluation
    * [CLIMATE-294] - Move existing normalization code over from RCMES toolkit
    * [CLIMATE-307] - Update OCW example runs to pull NC files from external source

** Bug
    * [CLIMATE-19] - Easy-RCMET fails on on copying py modules
    * [CLIMATE-225] - Add subplot functionality to draw_taylor_diagram
    * [CLIMATE-233] - Update UI to allow user to select file for subregions
    * [CLIMATE-240] - PredictiveFileBrowserInput doesn't update ng-model when user selects autocomplete option
    * [CLIMATE-250] - Variable Name error means 'ENS-MODEL' is not a choice within the rcmet/cli code
    * [CLIMATE-251] - Fix dataset selector pop up
    * [CLIMATE-252] - Redirect user to correct result page
    * [CLIMATE-253] - Easy_OCW tells the user to source an incorrect file
    * [CLIMATE-254] - Add Subregion Object to OCW
    * [CLIMATE-260] - decode_model_times chokes if time representation contains .0 after seconds
    * [CLIMATE-267] - Dataset doesn't validate input parameters on init
    * [CLIMATE-269] - Evaluation improperly imports other ocw package modules
    * [CLIMATE-272] - Local Cache in RCMES doesn't work properly
    * [CLIMATE-273] - test_local uses invalid import for data_source.local
    * [CLIMATE-275] - Timeline is not working with the new UI routing
    * [CLIMATE-277] - service '/static/evalResults/' should take a path 
    * [CLIMATE-278] - clean up UI 
    * [CLIMATE-283] - data_source.rcmed module doesn't properly mask data from the database
    * [CLIMATE-292] - Subregion Evaluation encloses results in an extra list
    * [CLIMATE-293] - Dataset processor needs to handle normalizing Dataset time values
    * [CLIMATE-299] - test_rcmed breaks if run outside of the tests directory
    * [CLIMATE-308] - test_local depends on NetCDF file in examples folder

** Improvement
    * [CLIMATE-12] - Update map drawing routine to draw dataset's actual bounds
    * [CLIMATE-31] - New RCMES Command line interface 
    * [CLIMATE-113] - Improve unit test coverage
    * [CLIMATE-149] - Update unit tests for directives
    * [CLIMATE-152] - New UI layout
    * [CLIMATE-214] - Add evaluation.py to OCW
    * [CLIMATE-238] - Allow users to set strings for colormaps in plotting functions
    * [CLIMATE-245] - Service to return list of images 
    * [CLIMATE-247] - Make the AngularJS UI easily skinnable
    * [CLIMATE-255] - Use Bounds object in dataset_processor.subset
    * [CLIMATE-256] - Use Bounds object in Evaluation
    * [CLIMATE-257] - Add Property for Evaluation.ref_dataset
    * [CLIMATE-258] - Improve Evaluation documentation
    * [CLIMATE-274] - Make the exception that the Dataset class throws more descriptive
    * [CLIMATE-276] - Refactor the dataset_processor.py code to no depend on toolkit.process
    * [CLIMATE-279] - rcmed.py returns a Dataset Object with a 4-D Array for the Dataset.values 
    * [CLIMATE-282] - Merge changes from CLIMATE-259 (RefactorPlots branch) into trunk
    * [CLIMATE-284] - Create separate Base Classes for metric.py
    * [CLIMATE-288] - Use parameter_id instead of logname to select observation in knmi_to_cru31_full_bias.py
    * [CLIMATE-295] - Change loggers so they don't use the root logger
    * [CLIMATE-296] - Log exception raises in dataset module
    * [CLIMATE-297] - test_local breaks if run outside of the tests directory
    * [CLIMATE-300] - Setup packaging
    * [CLIMATE-306] - Remove large OCW example NetCDF files

** New Feature
    * [CLIMATE-215] - Create new Plotter class for OCW refactoring
    * [CLIMATE-224] - Update the OCW UI with the AngularUI UI-Router
    * [CLIMATE-242] - Update run_rcmes_processing to support history
    * [CLIMATE-243] - Add capability to return a list of evaluation directories 
    * [CLIMATE-244] - Service to return list of images
    * [CLIMATE-249] - Add results/history page

** Task
    * [CLIMATE-20] - Easy-RCMET install requests JPL username / password for software dist
    * [CLIMATE-136] - Remove RCMET references from Easy-RCMET
    * [CLIMATE-213] - Create the dataset_processor.py module within the ocw folder
    * [CLIMATE-217] - Add metrics.py for OCW refactoring
    * [CLIMATE-218] - Update metric handling in Evaluation to coincide with new Metric definition
    * [CLIMATE-219] - Add name attribute to Dataset
    * [CLIMATE-239] - Remove Plotter class from plotter.py
    * [CLIMATE-301] - Fix licenses in obs4MIPs code
    * [CLIMATE-302] - Move obs4MIPs copyright headers
    * [CLIMATE-303] - Integrate obs4MIPs into OCW
    * [CLIMATE-304] - Add obs4MIPs JIRA component
    * [CLIMATE-305] - Update obs4MIPs setup.py with OCW related information
** Test
    * [CLIMATE-220] - implement unit tests for plotter.py



Release Notes - Apache Open Climate Workbench - Version 0.2-incubating

** Sub-task
    * [CLIMATE-139] - OCW dataset.py code
    * [CLIMATE-142] - OCW local.py code
    * [CLIMATE-185] - test_dataset.py

** Bug
    * [CLIMATE-140] - creating new "ocw"  directory in trunk
    * [CLIMATE-189] - PreviewMap directive assigns incorrect color to maps
    * [CLIMATE-191] - getResultDirInfo returns improper options
    * [CLIMATE-199] - Globe image import breaks on deploy
    * [CLIMATE-200] - Result.html needs to include angular-ui
    * [CLIMATE-201] - LeafletMap overlays aren't duplicated when the user scrolls the map
    * [CLIMATE-202] - Leaflet overlays aren't duplicated when user scrolls PreviewMaps
    * [CLIMATE-204] - Remove overlay display in the World Map
    * [CLIMATE-221] - checkLatLon in files.py doesn't work if lons are in the domain (180, 360)
    * [CLIMATE-226] - radmax parameter in __init__ is broken in utils.taylor.TaylorDiagram
    * [CLIMATE-229] - Formatting issue for monthly time series plots
    * [CLIMATE-232] - evaluation does not redirect to correct path

** Improvement
    * [CLIMATE-182] - Remove gray-ing of buttons in modal headers/footers
    * [CLIMATE-183] - Remove scrolling capability from timeline
    * [CLIMATE-184] - Add directive for adding thumbnail maps to dataset
    * [CLIMATE-187] - Add thumbnail map to dataset display
    * [CLIMATE-188] - Draw overlap border and user selected region on map
    * [CLIMATE-193] - Don't display dataset preview map when dataset is global
    * [CLIMATE-194] - Uncompiled Angular templating code is briefly present when page loads
    * [CLIMATE-195] - Timeline doesn't redraw when the window is resized
    * [CLIMATE-196] - "Powered by Leaflet" attribute on main map overlaps jQuery datepicker
    * [CLIMATE-197] - Add Angular-UI
    * [CLIMATE-198] - Add tooltips to UI buttons
    * [CLIMATE-205] - Improve user selected region display
    * [CLIMATE-206] - Add tooltip to dataset remove button
    * [CLIMATE-207] - Add background to settings modal
    * [CLIMATE-208] - Remove overlay color box from Dataset Display
    * [CLIMATE-209] - Set all PreviewMap overlays to the same color
    * [CLIMATE-210] - Move dataset re-grid option to Settings modal
    * [CLIMATE-211] - Clean up dataset display
    * [CLIMATE-222] - Update PredictiveFileBrowserInput.js to handle more then one case
    * [CLIMATE-223] - Update result.html to follow index.html style
    * [CLIMATE-234] - Make plotting functions consisted with new API documentation

** New Feature
    * [CLIMATE-128] - Adding Taylor Diagram support to plots
    * [CLIMATE-192] - creating new 'tests' directory under /trunk/ocw 
    * [CLIMATE-216] - Add new plotting functions to repository
    * [CLIMATE-231] - Add ability for plotter to process generic plotting functions


Release Notes - Apache Open Climate Workbench - Version 0.1-incubating

** Sub-task
    * [CLIMATE-11] - Move region-select parameters to a service
    * [CLIMATE-35] - Update dataset additions to include new display attribute
    * [CLIMATE-36] - Add checkbox to dataset display panels for toggling display attribute state
    * [CLIMATE-37] - Update map drawing routine to make drawing dataset overlays optional
    * [CLIMATE-40] - Add new re-gridding field when adding a dataset using the selectedDatasetInformation service
    * [CLIMATE-41] - Add re-gridding logic to the DatasetDisplayCtrl
    * [CLIMATE-42] - Add sliders for selecting lat/lon degree steps
    * [CLIMATE-46] - Add temporal re-grid to evaluation settings modal
    * [CLIMATE-48] - Update runEvaluation to use temporal re-grid option
    * [CLIMATE-57] - Add service for sharing evaluation settings
    * [CLIMATE-59] - Add modal for evaluation settings
    * [CLIMATE-60] - Add and wire-in SettingsCtrl
    * [CLIMATE-61] - Use new evaluation settings in runEvaluation
    * [CLIMATE-62] - Add checkbox for selecting re-grid options
    * [CLIMATE-63] - Add jQuery UI
    * [CLIMATE-65] - Add temporal regridding options to evaluationSettings service
    * [CLIMATE-69] - Add AngularUI date directive support
    * [CLIMATE-70] - Add new start and end datepickers
    * [CLIMATE-76] - Add parameter checks when user adjusts values in ParameterSelectCtrl
    * [CLIMATE-78] - WorldMapCtrl should allow for overlay redraw to be triggered via an event
    * [CLIMATE-80] - Trigger redraw of map overlays when user is finished typing.
    * [CLIMATE-81] - Don't watch region parameter changes to trigger map redraws
    * [CLIMATE-83] - Change ParameterSelectCtrl layout
    * [CLIMATE-84] - Hide UI control buttons instead of disabling them
    * [CLIMATE-85] - Evaluation button doesn't display properly when running an evaluation
    * [CLIMATE-94] - Move services in app.js to services.js
    * [CLIMATE-95] - Split up controllers.js
    * [CLIMATE-96] - Split up directives.js
    * [CLIMATE-98] - Remove filters.js
    * [CLIMATE-99] - Split up services.js
    * [CLIMATE-102] - Move services over to separate module
    * [CLIMATE-103] - Move directives over to a separate module
    * [CLIMATE-104] - Move controllers over to new module
    * [CLIMATE-109] - Get rid of useless boilerplate files
    * [CLIMATE-115] - Remove controllersSpec.js
    * [CLIMATE-116] - Add tests for ParameterSelectCtrl
    * [CLIMATE-120] - Make run/rcmes endpoint JSONP compatible
    * [CLIMATE-121] - Add tests for SettingsCtrl
    * [CLIMATE-122] - Add tests for DatasetDisplayCtrl
    * [CLIMATE-123] - Add tests for RcmedSelectionCtrl
    * [CLIMATE-130] - Add tests for ObservationSelectCtrl
    * [CLIMATE-131] - Add tests for WorldMapCtrl
    * [CLIMATE-133] - Remove unneeded timeline files
    * [CLIMATE-134] - Move timeline css file into appropriate lib folder
    * [CLIMATE-145] - Remove serviceSpec.js
    * [CLIMATE-146] - Add tests for EvaluationSettings service
    * [CLIMATE-147] - Add tests for RegionSelectParams service
    * [CLIMATE-148] - Add tests for SelectedDatasetInformation
    * [CLIMATE-150] - Remove directivesSpec.js
    * [CLIMATE-151] - Update BootstrapModal directive tests
    * [CLIMATE-154] - Remove filtersSpec.js
    * [CLIMATE-172] - Display evaluation results in a separate view
    * [CLIMATE-173] - Add service to return list of figures in work directory

** Bug
    * [CLIMATE-1] - Replace longName with longname to match the new JPL Webservice
    * [CLIMATE-5] - misc.py tried to import SubRegion when rcmet.py already has
    * [CLIMATE-14] - directory_helpers.py should prevent users from accessing arbitrary directories
    * [CLIMATE-18] - Easy-RCMET installs incorrect binary versions
    * [CLIMATE-21] - RCMES UI is unable to communicate with backend properly when directory access is limited
    * [CLIMATE-25] - bootstrap-modal keyboard escape doesn't work when an element isn't in focus
    * [CLIMATE-51] - Add style guide and information for new users
    * [CLIMATE-52] - Disable Parameter input boxes when the user hasn't selected a valid number of datasets
    * [CLIMATE-53] - db.extractData function should not change dir
    * [CLIMATE-58] - bootstrapModalOpen directive doesn't handle attributes correctly
    * [CLIMATE-64] - User is unable to uncheck regrid box
    * [CLIMATE-71] - Adding model dataset doesn't handle time values correctly
    * [CLIMATE-77] - User selected region is redrawn as the user types
    * [CLIMATE-79] - regionParameter changes cause a race condition when drawing map overlays
    * [CLIMATE-82] - checkParameters doesn't properly handle value comparisons
    * [CLIMATE-86] - Website - Update the Wiki link under Documentation 
    * [CLIMATE-87] - Easy-RCMET pulls repo from JPL instead of ASF
    * [CLIMATE-106] - requests module not installed by easy_rcmet
    * [CLIMATE-110] - Pull the 'raw_input' functions out of the metrics.calcPdf function
    * [CLIMATE-111] - Switch tests over to Karma
    * [CLIMATE-112] - Unit tests no longer work
    * [CLIMATE-118] - Update ParameterSelectCtrl datasets $watch to prevent call to undefined variable
    * [CLIMATE-126] - deprecated function is used in process.py
    * [CLIMATE-135] - zlib not installed to /usr/local
    * [CLIMATE-138] - calc_bias is undefined in metrics
    * [CLIMATE-141] - matplotlib is not imported in plots
    * [CLIMATE-158] - Basemap.cm is imported incorrectly in do_rcmes_processing_sub.py
    * [CLIMATE-159] - do_rcmes_procressing_sub breaks when graphing
    * [CLIMATE-167] - NetCDF4 change breaks list_vars service
    * [CLIMATE-168] - Refactored Functions in metrics.py return a different number of variables
    * [CLIMATE-169] - critical bugs in metrics.py and plots.py
    * [CLIMATE-170] - VM image does not work on AMD CPU based PC
    * [CLIMATE-175] - WorldMapCtrlTest is broken after addition of zooming map
    * [CLIMATE-177] - Update misc.select_metrics function to prevent user selection of incomplete metrics
    * [CLIMATE-181] - Timeline options don't work
    * [CLIMATE-186] - RCMES cannot handle NCEP reanalysis and GCM data 

** Documentation
    * [CLIMATE-157] - Replace PYTHON_PATH with PYTHONPATH in Easy-RCMET docs

** Improvement
    * [CLIMATE-9] - Move rootScope datasets object over to a service
    * [CLIMATE-10] - Move map-specific code to WorldMapCtrl
    * [CLIMATE-13] - Parameter selection in selectObservation.html needs to use proper databinding.
    * [CLIMATE-15] - Show upload confirmation when user submits local file to UI.
    * [CLIMATE-16] - Provide feedback when a dataset is submitted by the user
    * [CLIMATE-17] - Update bootstrap-modal directive to allow for animated open/closing
    * [CLIMATE-23] - bootstrap-modal and bootstrap-modal-open need refactored
    * [CLIMATE-24] - Mouse scroll needs to be disabled on the UI map
    * [CLIMATE-26] - Display the number of datasets currently queued for evaluation when the user is selecting datasets.
    * [CLIMATE-27] - Filter out invalid variable options in selectObservation
    * [CLIMATE-28] - Adjust how variable selection drop down boxes are displayed to the user depending on number of options
    * [CLIMATE-29] - Provide reasonable default options for drop downs to user when pulling datasets from RCMED
    * [CLIMATE-32] - Factor out host component of URLs for backend calls 
    * [CLIMATE-55] - Updating any modules using PyNgl and PyNio
    * [CLIMATE-66] - Clean up ParameterSelectCtrl
    * [CLIMATE-68] - Switch Start and End field over to jQuery UI DatePicker
    * [CLIMATE-72] - Adjust input parameter boxes display properties
    * [CLIMATE-73] - Remove Update button from ParameterSelectCtrl
    * [CLIMATE-74] - Add on-blur directive
    * [CLIMATE-75] - Parameter select input boxes need to reject invalid input
    * [CLIMATE-88] - Performance improvements for metrics.py
    * [CLIMATE-92] - Overhaul to plots.py
    * [CLIMATE-93] - Split up UI files for a more manageable code base
    * [CLIMATE-97] - Rename Leaflet Map directive
    * [CLIMATE-100] - Clean up JavaScript folder and imports
    * [CLIMATE-101] - Define controllers, directives, and services under separate modules
    * [CLIMATE-105] - Remove RCMES references in UI code
    * [CLIMATE-107] - All source files need ASF licence text
    * [CLIMATE-114] - Update unit tests for controllers
    * [CLIMATE-117] - updates to regridding
    * [CLIMATE-119] - Make ParameterSelectCtrl runEvaluation use Angular HTTP instead of jQuery
    * [CLIMATE-124] - Define RcmedSelectionCtrl.getObservations on scope instead of locally
    * [CLIMATE-125] - Define RcmedSelectionCtrl.getObservationTimeRange on scope
    * [CLIMATE-132] - Move JavaScript libs into appropriate folder
    * [CLIMATE-144] - Update unit tests for services
    * [CLIMATE-153] - Add filter for converting ISO dates to US dates
    * [CLIMATE-174] - Map should zoom to the overlap region of selected datasets
    * [CLIMATE-176] - Fix WorldMapCtrl indentation
    * [CLIMATE-178] - Fix TimelineCtrl indentation
    * [CLIMATE-180] - Timeline changes for new UI design
    * [CLIMATE-203] - Deprecate read_lolaT_from_file() in files.py
    * [CLIMATE-222] - Update PredictiveFileBrowserInput.js to handle more then one case
	* [CLIMATE-223] - Update results.html to follow index.html style 

** New Feature
    * [CLIMATE-33] - Add modal for metric selection
    * [CLIMATE-34] - Add ability to toggle dataset overlays
    * [CLIMATE-45] - Add ability for user to select temporal re-gridding options
    * [CLIMATE-67] - Add functionality to ingest locally stored hourly infrared temperature satellite data
    * [CLIMATE-89] - Implement a timeline widget 

** Task
    * [CLIMATE-3] - Purge Unnecessary JPL Internal Development Files/Folders
    * [CLIMATE-4] - Push latest code changes from JPL svn to Apache
    * [CLIMATE-6] - Add the Interactive Mode back into rcmet.py
    * [CLIMATE-108] - Clean up UI CSS files
    * [CLIMATE-129] - Create a KEYS files for GPG Code Signatures in trunk
    * [CLIMATE-155] - Update FontAwesome


Regional Climate Model Evaluation System
JIRA located here: https://oodt.jpl.nasa.gov/jira/browse/RCMES


Release Notes - RCMES Project - Version 1.1.0 - 08/09/2012

** The project has been renamed from Water Resource Management to Regional Climate Model Evaluation System


** Bug
    * [RCMES-59] - Drop Down Menu Lists are Broken @ http://rcmes.jpl.nasa.gov/
	* [RCMES-58] - set group ownership to 'daemon' for rcmes puny content
 	* [RCMES-46] - wrm_merra_slp - Database is being written to extremely slowly
 	* [RCMES-10] - Fix the MySQL/PHP Timeout for Database Query Web Service
 	* [RCMES-8] - AIRSL3NetCDF extractor should not extract 'data points' for parameter definitions
 	* [RCMES-7] - Granule Segments coming into the Catalog are being counted as new Granules
 	* [RCMES-6] - Update the Query API page to include datasetId
 	* [RCMES-4] - Catalog needs to insert the variable name into shortName instead of longName (parameter TABLE)
 	* [RCMES-3] - Granule Segments coming into the Catalog are being counted as new Datasets
 	* [RCMES-1] - ISO timestamp support in WRM means we need to change the TYPE of all time columns to VARCHAR20


** Improvement
    * [RCMES-42] - Rebrand SVN home for RCMES away from WRM
    * [RCMES-38] - Deploy RCMED under new URL
    * [RCMES-37] - Get PAR for RCMES
    * [RCMES-34] - Move mailing lists from wrm-general, wrm-dev, wrm-commits to rcmes-general, rcmes-dev and rcmes-commits
    * [RCMES-32] - Deploy RCMES main portal
    * [RCMES-31] - Drop un-used Tables from WRM_PROD database
 
 
 ** New Feature
    * [RCMES-13] - Create a met extractor for AIRS NetCDF files
    * [RCMES-12] - Python Query API for controlled access to the WRM infrastructure via Python scripts


** Task
 	* [RCMES-49] - 17 more Databases Needed for the RCMED
 	* [RCMES-48] - Create 10 more Databases
 	* [RCMES-44] - Create A set of Databases for the MERRA dataset
 	* [RCMES-28] - Schema and supporting doc. checked into SVN
 	* [RCMES-26] - File Manager Policy checked into SVN
 	* [RCMES-24] - Each Parameter needs a TIMESTEP Metadata Key with a single value from a restricted list.
 	* [RCMES-20] - Update - Python GRIB Extractor to read all variables in a file
 	* [RCMES-18] - Enable GRIB Extractor to take in Command Line Arguments
 	* [RCMES-17] - Set up basic website that provides information about the contents of the WRM databse
 	* [RCMES-16] - Develop metadata extractor for sample data


WRM Regional Climate Model Evaluation Database
JIRA located here:  http://oodt.jpl.nasa.gov/jira/browse/WRM


Release Notes - Water Resource Management Infrastructure - Version 1.0.0 - 09/24/2010


** Bug
    * [WRM-9] - AIRSL3NetCDF extractor should not extract 'data points' for parameter definitions
    * [WRM-13] - Granule Segments coming into the Catalog are being counted as new Granules
    * [WRM-14] - Granule Segments coming into the Catalog are being counted as new Datasets
    * [WRM-15] - ISO timestamp support in WRM means we need to change the TYPE of all time columns to VARCHAR20
    * [WRM-16] - Catalog needs to insert the variable name into shortName instead of longName (parameter TABLE)


** New Feature
    * [WRM-8] - Create a met extractor for AIRS NetCDF files
    * [WRM-10] - Python Query API for controlled access to the WRM infrastructure via Python scripts

** Task
    * [WRM-1] - File Manager Policy checked into SVN
    * [WRM-2] - Schema and supporting doc. checked into SVN
    * [WRM-3] - Develop metadata extractor for sample data
    * [WRM-4] - Develop a config script for running the ExternMetExtractor
    * [WRM-5] - Create JIRA Components to represent the different aspects of the WRM project
    * [WRM-6] - Create a development structure in SVN that reflects all aspects of project effort
    * [WRM-7] - Create a deployment process that makes it easy to quickly build a working production environment
    * [WRM-12] - Enable GRIB Extractor to take in Command Line Arguments
    * [WRM-17] - Set up basic website that provides information about the contents of the WRM databse

