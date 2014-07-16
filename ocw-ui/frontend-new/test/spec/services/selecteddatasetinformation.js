'use strict';

describe('Service: selectedDatasetInformation', function () {

  // load the service's module
  beforeEach(module('ocwUiApp'));

  // instantiate service
  var selectedDatasetInformation;
  beforeEach(inject(function (_selectedDatasetInformation_) {
    selectedDatasetInformation = _selectedDatasetInformation_;
  }));

  it('should do something', function () {
    expect(!!selectedDatasetInformation).toBe(true);
  });

});
