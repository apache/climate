'use strict';

describe('Directive: bootstrapModalOpen', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<bootstrap-modal-open></bootstrap-modal-open>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the bootstrapModalOpen directive');
  }));
});
