'use strict';

/**
 * @ngdoc service
 * @name ocwUiApp.selectedDatasetInformation
 * @description
 * # selectedDatasetInformation
 * Service in the ocwUiApp.
 */
angular.module('ocwUiApp')
.service('selectedDatasetInformation', function() {
	var datasets = [];

	return {
		getDatasets: function() {
			return datasets;
		},
		getDatasetCount: function() {
			return datasets.length;
		},
		// TODO: Define the structure of the objects that are added with addDataset.
		addDataset: function(dataset) {
			// All datasets need a shouldDisplay attribute that is used when rendering
			// the overlays on the map!
			dataset.shouldDisplay = false;
			// The regrid attribute indicates which dataset should be used for spatial regridding
			dataset.regrid = false;

			datasets.push(dataset);
		},
		removeDataset: function(index) {
			datasets.splice(index, 1);
		},
		clearDatasets: function() {
			datasets.length = 0;
		},
	};
});
