'use strict';

describe('Controller: RcmedselectionCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var RcmedselectionCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    RcmedselectionCtrl = $controller('RcmedselectionCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
