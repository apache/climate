'use strict';

describe('Controller: ParameterselectCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var ParameterselectCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ParameterselectCtrl = $controller('ParameterselectCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
