'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:DatasetDisplayCtrl
 * @description
 * # DatasetDisplayCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
  .controller('DatasetDisplayCtrl', ['$rootScope', '$scope', 'selectedDatasetInformation', 
    function($rootScope, $scope, selectedDatasetInformation) {
	$scope.datasets = selectedDatasetInformation.getDatasets();

	$scope.removeDataset = function($index) {
	  selectedDatasetInformation.removeDataset($index);
	}

	$scope.setRegridBase = function(index) {
      for (var i = 0; i < $scope.datasets.length; i++) {
        $scope.datasets[i].regrid = ((i == index) ? $scope.datasets[i].regrid : false);
      }
	}
}]);
