'use strict';

/**
 * @ngdoc overview
 * @name ocwUiApp
 * @description
 * # ocwUiApp
 *
 * Main module of the application.
 */
angular
  .module('ocwUiApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ui.router',
    'ui.bootstrap'
  ])
  .config(['$stateProvider', '$routeProvider', '$urlRouterProvider',
    function ($stateProvider,   $routeProvider,   $urlRouterProvider) {
      $urlRouterProvider
        .when('/r?id', '/results/:id')
        .otherwise('/');

      $routeProvider
        .when('/evaluation/:id', {
          redirectTo: '/results/:id',
        })
        .when('/', {
          redirectTo: '/evaluate',
        });

      $stateProvider
        .state('main',{
          url: '/evaluate',
          templateUrl: 'views/main.html',
        })
        .state('results', {
          url: '/results',
          abstract: true,
          templateUrl: 'views/results.html',
          controller: 'ResultCtrl'
        })
        .state('results.list', {
          // parent: 'results',
          url: '',
          templateUrl: 'views/resultslist.html',
        })
        .state('results.detail', {
          // parent: 'results',
          url: '/{resultId}',
          views: {
            '': {
              templateUrl: 'views/resultsdetail.html',
              controller: 'ResultDetailCtrl'
            },
            'menu': {
              templateProvider:
                [ '$stateParams',
                function ($stateParams){
                  return '<hr><small class="muted">result ID: ' + $stateParams.resultId + '</small>';
                }],
            },
          },
        });
    }])
  .run(['$rootScope', '$state', '$stateParams',
    function ($rootScope,   $state,   $stateParams) {
      $rootScope.$state = $state;
      $rootScope.$stateParams = $stateParams;
      $rootScope.evalResults = '';
      $rootScope.fillColors = ['#ff0000', '#00c90d', '#cd0074', '#f3fd00'];
      $rootScope.surroundColors = ['#a60000', '#008209', '#8f004b', '#93a400'];
      $rootScope.baseURL = 'http://localhost:8082';
  }]);
