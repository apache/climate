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
});
