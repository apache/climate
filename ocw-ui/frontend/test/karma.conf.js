// Karma configuration
// http://karma-runner.github.io/0.12/config/configuration-file.html
// Generated on 2014-07-15 using
// generator-karma 0.8.3

module.exports = function(config) {
  'use strict';

  config.set({
    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // base path, that will be used to resolve files and exclude
    basePath: '../',

    // testing framework to use (jasmine/mocha/qunit/...)
    frameworks: ['jasmine'],

    // list of files / patterns to load in the browser
    files: [
      'bower_components/angular/angular.js',
      'bower_components/angular-mocks/angular-mocks.js',
      'bower_components/angular-animate/angular-animate.js',
      'bower_components/angular-cookies/angular-cookies.js',
      'bower_components/angular-resource/angular-resource.js',
      'bower_components/angular-route/angular-route.js',
      'bower_components/angular-animate/angular-animate.js',
      'bower_components/angular-bootstrap/ui-bootstrap.js',
      // For some reason this causes the tests to completely fail to run
      // if it is uncommented.
      //'bower_components/angular-scenario/angular-scenario.js',
      'bower_components/angular-ui-date/src/date.js',
      'bower_components/angular-ui-router/release/angular-ui-router.js',
      'bower_components/chap-links-timeline/timeline.js',
      'bower_components/jquery/dist/jquery.js',
      'bower_components/jquery-ui/jquery-ui.js',
      'bower_components/leaflet/dist/leaflet.js',
      'app/scripts/**/*.js',
      'test/mock/**/*.js',
      'test/spec/**/*.js'
    ],

    // list of files / patterns to exclude
    exclude: [],

    // web server port
    port: 8080,


    // Start these browsers, currently available:
    // - Chrome
    // - Firefox
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    // Ok to leave this empty as karma-detect-browsers will figure this out based on what is installed.
    // Either set enabled to false for karma-detect-browsers and fill in a specific list or update
    // the logic in the karma-detect-browsers config to remove those you don't want to test.
    browsers: [ ],

    frameworks: ['jasmine', 'detectBrowsers'],

    detectBrowsers: {
      // enable/disable, default is true
      enabled: true,

      // enable/disable phantomjs support, default is true
      usePhantomJS: true,

      // post processing of browsers list
      // here you can edit the list of browsers used by karma
      postDetection: function(availableBrowser) {

          var result = availableBrowser;

          //Remove PhantomJS if another browser has been detected
          //if (availableBrowser.length > 1 && availableBrowser.indexOf('PhantomJS')>-1) {
          //  var i = result.indexOf('PhantomJS');

          //  if (i !== -1) {
          //    result.splice(i, 1);
          //  }
          //}

          return result;
        }
    },

    // Which plugins to enable
    plugins: [
      'karma-phantomjs-launcher',
      'karma-chrome-launcher',
      'karma-firefox-launcher',
      'karma-safari-launcher',
      'karma-ie-launcher',
      'karma-detect-browsers',
      'karma-jasmine'
    ],

    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false,

    colors: true,

    // level of logging
    // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
    logLevel: config.LOG_INFO,

    // Uncomment the following lines if you are using grunt's server to run the tests
    // proxies: {
    //   '/': 'http://localhost:9000/'
    // },
    // URL root prevent conflicts with the site root
    // urlRoot: '_karma_'
  });
};
