'use strict';

/**
 * @ngdoc directive
 * @name ocwUiApp.directive:bootstrapModalOpen
 * @description
 * # bootstrapModalOpen
 */
angular.module('ocwUiApp')
.directive('bootstrapModalOpen', function() {
	return {
		restrict: 'A',
		link: function(scope, elem, attrs) {
			// Default to showing the background if the user didn't specify a value for this.
			var hasBackground = (attrs.background === undefined ? true : (attrs.background == "true"));
			// Enable keyboard closing of modal with escape key.
			var hasKeyboardEscape = (attrs.keyboard === undefined ? true : (attrs.keyboard == "true"));

			$(elem).bind('click', function() {
				$('#' + attrs.bootstrapModalOpen).trigger('modalOpen', [hasBackground, hasKeyboardEscape]);
			});
		}
	};
});
