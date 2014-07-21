'use strict';

/**
 * @ngdoc service
 * @name ocwUiApp.regionSelectParams
 * @description
 * # regionSelectParams
 * Service in the ocwUiApp.
 */
angular.module('ocwUiApp')
.service('regionSelectParams', function() {
	var parameters = {
		"areValid" : true,
		"latMin"   : "",
		"latMax"   : "",
		"lonMin"   : "",
		"lonMax"   : "",
		"start"    : "",
		"end"      : "",
	};

	return {
		getParameters: function() {
			return parameters;
		},
	};
});
