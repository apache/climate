'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:ResultCtrl
 * @description
 * # ResultCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
.controller('ResultCtrl', ['$rootScope', '$scope', '$http',
function($rootScope, $scope, $http) {

    $scope.results = [];

    // Get all evaluation directories
    $http.jsonp($rootScope.baseURL + '/dir/results/?callback=JSON_CALLBACK')
    .success(function(data) {
      data = data['listing']

      var cacheDirIndex = data.indexOf("/cache");
      if (cacheDirIndex > -1) {
        data.split(cacheDirIndex, 1)
      }

      $scope.results = data.sort().reverse();
    });
}]);
