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

describe('Controller: DatasetDisplayCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var DatasetdisplayctrlCtrl,
      scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DatasetdisplayctrlCtrl = $controller('DatasetDisplayCtrl', {
      $scope: scope
    });
  }));

  it('should initialize the removeDataset function', function() {
    scope.datasets.push(1);
    scope.datasets.push(2);

    expect(scope.datasets[0]).toBe(1);

    scope.removeDataset(0);

    expect(scope.datasets[0]).toBe(2);
  });

  it('should initialize the removeDataset function', function() {
    scope.datasets.push(1);
    scope.datasets.push(2);

    expect(scope.datasets[0]).toBe(1);

    scope.removeDataset(0);

    expect(scope.datasets[0]).toBe(2);
  });
});
