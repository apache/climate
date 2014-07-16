'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:ResultDetailCtrl
 * @description
 * # ResultDetailCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
.controller('ResultDetailCtrl', ['$rootScope', '$scope', '$http', '$stateParams',
function($rootScope, $scope, $http, $stateParams) {
	$scope.result = $stateParams.resultId;
	
	$http.jsonp($rootScope.baseURL + '/dir/results/' + $scope.result + '?callback=JSON_CALLBACK')
	.success(function(data) {
		data = data['listing'];

		if (data.length < 1) {
			$scope.figures = null;
			$scope.alertMessage = "No results found.";
			$scope.alertClass = "alert alert-danger";
		} else {
			$scope.figures = data;
		}
	});
}]);
