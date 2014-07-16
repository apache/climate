'use strict';

/**
 * @ngdoc directive
 * @name ocwUiApp.directive:timeline
 * @description
 * # timeline
 */
angular.module('ocwUiApp')
.directive('timeline', function($rootScope, $window) {
	return {
		restrict: 'C',
		replace: true,
		transclude: true,
		template: '<div id="OCWtimeline"></div>',
		link: function(scope, element, attrs) {
			// Instantiate timeline object.
			$rootScope.timeline = new links.Timeline(document.getElementById('OCWtimeline'));

			// Redraw the timeline whenever the window is resized
			angular.element($window).bind('resize', function() {
				$rootScope.timeline.checkResize();
			});

			var options = {
				"width": "100%",
				"showCurrentTime": false,
				"moveable": false,
				"zoomable": false
			};

			$rootScope.timeline.draw([], options);
		}
	}
});
