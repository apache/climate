'use strict';

describe('Filter: ISODateToMiddleEndian', function () {

  // load the filter's module
  beforeEach(module('ocwUiApp'));

  // initialize a new instance of the filter before each test
  var ISODateToMiddleEndian;
  beforeEach(inject(function ($filter) {
    ISODateToMiddleEndian = $filter('ISODateToMiddleEndian');
  }));

  it('should return the input prefixed with "ISODateToMiddleEndian filter:"', function () {
    var text = 'angularjs';
    expect(ISODateToMiddleEndian(text)).toBe('ISODateToMiddleEndian filter: ' + text);
  });

});
