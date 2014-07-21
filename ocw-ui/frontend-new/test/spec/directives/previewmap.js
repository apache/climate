'use strict';

describe('Directive: previewMap', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<preview-map></preview-map>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the previewMap directive');
  }));
});
