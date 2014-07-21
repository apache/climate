'use strict';

/**
 * @ngdoc filter
 * @name ocwUiApp.filter:ISODateToMiddleEndian
 * @function
 * @description
 * # ISODateToMiddleEndian
 * Filter in the ocwUiApp.
 */
angular.module('ocwUiApp')
.filter('ISODateToMiddleEndian', function() {
	return function(input) {
		var original = input;

		// Strip whitespace from the start and end of the string
		input = input.replace(/(^\s+|\s+$)/g, '');

		// ISO Standard says time is separated from Date with a 'T'. Our timestamps
		// slightly modify that and use a space. We'll check for both here and prefer
		// to split on a 'T' if it's available.
		if (input.indexOf('T') != -1 || input.indexOf(' ') != -1) {
			input = (input.indexOf('T') != -1) ? input.split('T')[0] : input.split(' ')[0];
		} 
		
		// The components of the date should be split with hyphens. If we can't find them
		// then the string is poorly formed.
		if (input.indexOf('-') == -1 || input.split('-').length - 1 != 2) {
			return original;
		}

		// At this point the date is probably valid and we should try to convert it!
		var components = input.split('-');
		return (components[1] + "/" + components[2] + "/" + components[0]);
	};
});
