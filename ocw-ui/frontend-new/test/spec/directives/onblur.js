'use strict';

describe('Directive: onBlur', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<on-blur></on-blur>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the onBlur directive');
  }));
});
