'use strict';

describe('Controller: WorldmapCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var WorldmapCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    WorldmapCtrl = $controller('WorldmapCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
