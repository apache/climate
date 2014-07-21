'use strict';

describe('Controller: DatasetdisplayctrlCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var DatasetdisplayctrlCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DatasetdisplayctrlCtrl = $controller('DatasetdisplayctrlCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
