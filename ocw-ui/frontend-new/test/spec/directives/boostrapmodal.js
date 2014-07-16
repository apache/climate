'use strict';

describe('Directive: boostrapModal', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<boostrap-modal></boostrap-modal>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the boostrapModal directive');
  }));
});
