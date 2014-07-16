'use strict';

describe('Controller: ObservationselectCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var ObservationselectCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ObservationselectCtrl = $controller('ObservationselectCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
