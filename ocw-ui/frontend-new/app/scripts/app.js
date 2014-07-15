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
    'ngRoute'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
