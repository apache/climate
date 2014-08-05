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

describe('Directive: onBlur', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should call the supplied function on the blur event', function() {
    inject(function($compile) {
      // Set a scope variable to make sure that on-blur calls 
      // the function that we pass to it.
      scope.bogusFunction = function() {
        scope.test = "hi"
      }

      var element = angular.element('<input on-blur="bogusFunction();" />')
      element = $compile(element)(scope)

      expect(scope.test).toNotBe('hi');
      element.triggerHandler('blur');
      expect(scope.test).toBe('hi');
    });
  });
});
