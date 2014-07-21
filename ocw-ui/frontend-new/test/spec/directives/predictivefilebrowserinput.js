'use strict';

describe('Directive: predictiveFileBrowserInput', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<predictive-file-browser-input></predictive-file-browser-input>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the predictiveFileBrowserInput directive');
  }));
});
