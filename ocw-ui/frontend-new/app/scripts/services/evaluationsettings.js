'use strict';

/**
 * @ngdoc service
 * @name ocwUiApp.evaluationSettings
 * @description
 * # evaluationSettings
 * Service in the ocwUiApp.
 */
angular.module('ocwUiApp')
.service('evaluationSettings', function($rootScope, $http) {
    $http.get($rootScope.baseURL + '/processing/metrics/').then(function(data) {
        metrics_data = data['data']['metrics'];
        metrics = [];

        for (var i = 0; i < metrics_data.length; ++i) {
            metrics.push({'name': metrics_data[i], 'select': false});
        }

        settings['metrics'] = metrics;
    });

	var settings = {
        'metrics': [],
		'temporal': {
			'options': ['daily', 'monthly', 'yearly'],
			'selected': 'yearly',
		},
		'spatialSelect': null,
	};

	return {
		getSettings: function() {
			return settings;
		}
	};
});		
