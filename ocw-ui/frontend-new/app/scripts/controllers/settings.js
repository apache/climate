'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:SettingsCtrl
 * @description
 * # SettingsCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
.controller('SettingsCtrl', ['$scope', 'evaluationSettings', 'selectedDatasetInformation',
function($scope, evaluationSettings, selectedDatasetInformation) {
	$scope.settings = evaluationSettings.getSettings();
	$scope.datasets = selectedDatasetInformation.getDatasets();
}]);
