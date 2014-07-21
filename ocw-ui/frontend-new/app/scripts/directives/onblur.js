'use strict';

/**
 * @ngdoc directive
 * @name ocwUiApp.directive:onBlur
 * @description
 * # onBlur
 */
angular.module('ocwUiApp')
.directive('onBlur', function() {
	return {
        restrict: 'A',
        link: function($scope, $elem, $attrs) {
            $elem.bind('blur', function() {
				$scope.$eval($attrs.onBlur);
			});
        },
    };
});
