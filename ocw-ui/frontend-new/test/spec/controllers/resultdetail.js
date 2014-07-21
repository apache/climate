'use strict';

describe('Controller: ResultdetailCtrl', function () {

  // load the controller's module
  beforeEach(module('ocwUiApp'));

  var ResultdetailCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ResultdetailCtrl = $controller('ResultdetailCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
