'use strict';

describe('Controller: ResultCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var ResultCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ResultCtrl = $controller('ResultCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
