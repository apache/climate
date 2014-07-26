/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

'use strict';

describe('Controller: ParameterSelectCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var ParameterselectCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ParameterselectCtrl = $controller('ParameterSelectCtrl', {
      $scope: scope
    });
  }));

  it('should initialize spatial and temporal range default values properly', function() {
    expect(scope.latMin).toBe(-90);
    expect(scope.latMax).toBe(90);
    expect(scope.lonMin).toBe(-180);
    expect(scope.lonMax).toBe(180);
    expect(scope.start).toBe("1900-01-01 00:00:00");
    expect(scope.end).toBe("2030-01-01 00:00:00");
  });

  it('should grab the default set of selected datasets from the service', function() {
    // We should get an object with no keys since the user hasn't selected any
    // datasets by default. Object.keys returns an array of all the user defined
    // keys in the object.
    expect(typeof scope.datasets).toBe('object');
    expect(Object.keys(scope.datasets).length).toBe(0);
  });

  it('should grab the default region select param object from the regionSelectParams service', function() {
    // The default display values aren't going to be changing any time soon. This test 
    // is a bit of a duplicate since this is really testing functionality of the service.
    // Can't hurt to make sure that we're getting results though!
    expect(typeof scope.displayParams).toBe('object');
    expect(Object.keys(scope.displayParams).length).toBe(7);
  });

  it('should initialize misc. values properly', function() {
    expect(scope.runningEval).toBe(false);
    expect(scope.areInUserRegridState).toBe(false);
    expect(scope.latSliderVal).toBe(0);
    expect(scope.lonSliderVal).toBe(0);
  });

  it('should set the default datepicker settings', function() {
    // This tests the default values that get passed to the datepicker objects that we
    // initialize with a directive.
    expect(Object.keys(scope.datepickerSettings).length).toBe(2);
    expect(scope.datepickerSettings.changeMonth).toBe(true);
    expect(scope.datepickerSettings.changeYear).toBe(true);
  });

  it('should initialize the control disable function', function() {
    // Add to dummy values to datasets to make sure the disable function
    // triggers properly.
    scope.datasets.push(1);
    scope.datasets.push(2);
    expect(scope.shouldDisableControls()).toBe(false);
  });

  it('should initialize the disable evaluation button function', function() {
    expect(scope.shouldDisableEvaluateButton()).toBe(true);
    scope.datasets.push(1);
    expect(scope.shouldDisableEvaluateButton()).toBe(true);
    scope.datasets.push(2);
    expect(scope.shouldDisableEvaluateButton()).toBe(false);
    scope.runningEval = true;
    expect(scope.shouldDisableEvaluateButton()).toBe(true);
  });

  it('should initialize the disable results view function', function() {
    inject(function($rootScope) {
      expect(scope.shouldDisableResultsView()).toBe(true);

      // Set evalResults to something other than the default value
      $rootScope.evalResults = "this is not an empty string";

      expect(scope.shouldDisableResultsView()).toBe(false);
    });
  });

  /*
   * TODO: $scope.$apply() in the controller is breaking this test. Need to
   * find a way to deal with that or rethink how we handle this test.
   *
   */
  /*
  it('should initialize the check parameters function', function() {
      // Set the displayParams values to be "out of bounds" values so checkParams 
      // adjusts them properly.
      scope.displayParams.latMin = "-95";
      scope.displayParams.latMax = "95";
      scope.displayParams.lonMin = "-185";
      scope.displayParams.lonMax = "185";
      scope.displayParams.start = "1980-00-00 00:00:00";
      scope.displayParams.end = "2031-01-01 00:00:00";

      // If we don't remove the watch on datasets we end up with displayParam values 
      // all being undefined (but only during testing, which is odd...)
      scope.unwatchDatasets();
      scope.checkParameters();

      expect(scope.displayParams.latMin).toBe(-90);
      expect(scope.displayParams.latMax).toBe(90);
      expect(scope.displayParams.lonMin).toBe(-180);
      expect(scope.displayParams.lonMax).toBe(180);
      expect(scope.displayParams.start).toBe('1980-01-01 00:00:00');
      expect(scope.displayParams.end).toBe('2030-01-01 00:00:00');
  });
  */

  /*
   * TODO: The backend call for this expects completely different data formats.
   * Additionally, there are many more URLs to mock now. Something has definitely
   * changed with how httpBackend functions or the way the code base is setup.
   */
  /*
  it('should properly set the results of running an evaluation', function() {
    inject(function($rootScope, $controller, $httpBackend) {
      var scope = $rootScope.$new();
      var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

      // Seed rootScope with a known URL for test queries and holder for eval results
      $rootScope.baseURL = "http://localhost:9876";
      $rootScope.evalResults = {};

      // Seed the displayParams so the query is properly formatted
      scope.displayParams.lonMin = -180;
      scope.displayParams.lonMax = 180;
      scope.displayParams.latMin = -90;
      scope.displayParams.latMax = 90;
      scope.displayParams.start = "1980-01-01";
      scope.displayParams.end = "2030-01-01";

      // The expected URL string that the frontend generates given this example set
      var urlString = "http://localhost:9876/rcmes/run/?" + 
        "callback=JSON_CALLBACK&" + 
        "endTime=2030-01-01%2000%3A00%3A00&" +
        "filelist=%2Fusr%2Flocal%2Frcmes%2FmodelsForUI%2Fprec.HRM3.ncep.monavg.nc&" +
        "latMax=90&" +
        "latMin=-90&" +
        "lonMax=180&" +
        "lonMin=-180&" +
        "metricOption=bias&" +
        "modelLatVarName=lat&" +
        "modelLonVarName=lon&" +
        "modelTimeVarName=time&" +
        "modelVarName=prec&" +
        "obsDatasetId=3&" +
        "obsParameterId=36&" +
        "regridOption=model&" +
        "startTime=1980-01-01%2000%3A00%3A00&" +
        "timeRegridOption=monthly";

      // Example dataset configuration for the test.
      scope.datasets = [
        {
          "isObs"         : 1,
          "id"            : "3",
          "name"          : "Tropical Rainfall Measuring Mission Dataset",
          "param"         : "36",
          "paramName"     : "TRMM v.6 Monthly Precipitation",
          "latlonVals"    : {"latMin" : -90, "latMax" : 90, "lonMin" : -180, "lonMax" : 180},
          "lat"           : "N/A",
          "lon"           : "N/A",
          "timeVals"      : {"start" : "1998-01-01 00:00:00",
          "end"           : "2010-01-01 00:00:00"},
          "time"          : "N/A",
          "shouldDisplay" : true,
          "regrid"        : false
          },{
          "isObs"         : 0,
          "id"            : "/usr/local/rcmes/modelsForUI/prec.HRM3.ncep.monavg.nc",
          "name"          : "prec.HRM3.ncep.monavg.nc",
          "param"         : "prec",
          "paramName"     : "prec",
          "lat"           : "lat",
          "lon"           : "lon",
          "latlonVals"    : {"latMin" : "15.25",
          "latMax"        : "75.25",
          "lonMin"        : "-159.75",
          "lonMax"        : "-29.75"},
          "time"          : "time",
          "timeVals"      : {"start":"1980-01-01 00:00:00",
          "end"           : "2004-12-01 00:00:00"},
          "shouldDisplay" : true,
          "regrid"        : false
        }
      ];

      $httpBackend.expectGET('http://localhost:8082/processing/metrics/').respond(
        200, {'data': {'metrics': ['foo', 'bar']}}
      )
      $httpBackend.expectPOST('http://localhost:9876/processing/run_evaluation/').respond(200) 
      $httpBackend.expectGET('views/main.html').respond(200)
      $httpBackend.expectJSONP(urlString).respond(200, 
          {'comparisonPath': '/fake/path1', 
           'modelPath': '/fake/path2', 
           'obsPath': '/fake/path3'});

      console.log('here')
      scope.runEvaluation();
      console.log('here1')
      $httpBackend.flush();
      console.log('here2')

      expect($rootScope.evalResults.comparisonPath).toBe('path1');
      expect($rootScope.evalResults.modelPath).toBe('path2');
      expect($rootScope.evalResults.obsPath).toBe('path3');
    });
  });
  */
});
