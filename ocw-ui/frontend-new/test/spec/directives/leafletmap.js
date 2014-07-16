'use strict';

describe('Directive: leafletMap', function () {

  // load the directive's module
  beforeEach(module('ocwUiApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<leaflet-map></leaflet-map>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the leafletMap directive');
  }));
});
