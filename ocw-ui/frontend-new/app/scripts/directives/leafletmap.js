'use strict';

/**
 * @ngdoc directive
 * @name ocwUiApp.directive:leafletMap
 * @description
 * # leafletMap
 */
angular.module('ocwUiApp')
.directive('leafletMap', function($rootScope) {
	return {
		restrict: 'E',
		replace: true,
		template: '<div></div>',
		link: function(scope, element, attrs) {
			$rootScope.map = L.map(attrs.id, {
				center: [40, 0],
				zoom: 2,
				scrollWheelZoom: false,
				attributionControl: false,
				worldCopyJump: true,
			});

			L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {}).addTo($rootScope.map);
		}
	};
});
