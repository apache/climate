'use strict';

describe('Service: evaluationSettings', function () {

  // load the service's module
  beforeEach(module('ocwUiApp'));

  // instantiate service
  var evaluationSettings;
  beforeEach(inject(function (_evaluationSettings_) {
    evaluationSettings = _evaluationSettings_;
  }));

  it('should do something', function () {
    expect(!!evaluationSettings).toBe(true);
  });

});
