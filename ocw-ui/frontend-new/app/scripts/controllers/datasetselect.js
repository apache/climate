'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:DatasetSelectCtrl
 * @description
 * # DatasetSelectCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
  .controller('DatasetSelectCtrl', ['$scope', 'selectedDatasetInformation',
    function($scope, selectedDatasetInformation) {
      // Grab a copy of the datasets so we can display a count to the user!
      $scope.datasetCount = selectedDatasetInformation.getDatasets();

      $scope.shouldDisableClearButton = function() {
        return (selectedDatasetInformation.getDatasetCount() === 0);
      };

      $scope.clearDatasets = function() {
        selectedDatasetInformation.clearDatasets();
      };

      $scope.open = function () {
        $scope.datasetSelect = true;
      };

      $scope.close = function () {
        $scope.datasetSelect = false;
      };

      $scope.opts = {
        backdropFade: true,
        dialogFade: true,
      };

      $scope.templates = [
        {title:'Local File', url: 'views/selectobservation.html'},
        {title:'RCMED', url: 'views/selectrcmed.html'},
        {title:'ESG', disabled: true}
      ];

      $scope.template = $scope.templates[0];
    }
  ]);
