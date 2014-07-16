'use strict';

describe('Controller: DatasetselectCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var DatasetselectCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DatasetselectCtrl = $controller('DatasetselectCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
