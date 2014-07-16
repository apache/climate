'use strict';

describe('Service: regionSelectParams', function () {

  // load the service's module
  beforeEach(module('ocwUiApp'));

  // instantiate service
  var regionSelectParams;
  beforeEach(inject(function (_regionSelectParams_) {
    regionSelectParams = _regionSelectParams_;
  }));

  it('should do something', function () {
    expect(!!regionSelectParams).toBe(true);
  });

});
