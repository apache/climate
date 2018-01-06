/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

'use strict';

describe('Service: selectedDatasetInformation', function () {

  // load the service's module
  beforeEach(module('ocwUiApp'));

  // instantiate service
  var selectedDatasetInformation;
  beforeEach(inject(function (_selectedDatasetInformation_) {
    selectedDatasetInformation = _selectedDatasetInformation_;
  }));

  it('should initialize the selectedDatasetInformation service', function() {
    inject(function(selectedDatasetInformation) {
      expect(selectedDatasetInformation).not.toEqual(null);
    });
  });

  it('should provide the getDatasets function', function() {
    inject(function(selectedDatasetInformation) {
      expect(selectedDatasetInformation.getDatasets()).not.toEqual(null);
    });
  });

  it('should provide the getDatasetCount function', function() {
    inject(function(selectedDatasetInformation) {
      expect(selectedDatasetInformation.getDatasetCount()).toEqual(0);
    });
  });

  it('should provide the addDataset function', function() {
    inject(function(selectedDatasetInformation) {
      selectedDatasetInformation.addDataset({});
      expect(selectedDatasetInformation.getDatasetCount()).toEqual(1);
    });
  });

  it('should set the shouldDisplay attribute when adding a dataset', function() {
    inject(function(selectedDatasetInformation) {
      selectedDatasetInformation.addDataset({});
      expect(selectedDatasetInformation.getDatasets()[0].shouldDisplay).toBe(false);
    });
  });

  it('should set the regrid attribute when adding a dataset', function() {
    inject(function(selectedDatasetInformation) {
      selectedDatasetInformation.addDataset({});
      expect(selectedDatasetInformation.getDatasets()[0].regrid).toBe(false);
    });
  });

  it('should provide the removeDataset function', function() {
    inject(function(selectedDatasetInformation) {

      var dataset_1 = {name: 'dataset_1', shouldDisplay: false, regrid: false};
      var dataset_2 = {name: 'dataset_2', shouldDisplay: false, regrid: false};

      selectedDatasetInformation.addDataset(dataset_1);
      selectedDatasetInformation.addDataset(dataset_2);

      expect(selectedDatasetInformation.getDatasets()[0]).toEqual(dataset_1);
      selectedDatasetInformation.removeDataset(0);
      expect(selectedDatasetInformation.getDatasets()[0]).toEqual(dataset_2);
    });
  });

  it('should provide the clearDatasets function', function() {
    inject(function(selectedDatasetInformation) {
      selectedDatasetInformation.addDataset({});
      expect(selectedDatasetInformation.getDatasetCount()).toEqual(1);

      selectedDatasetInformation.clearDatasets();
      expect(selectedDatasetInformation.getDatasetCount()).toEqual(0);
    });
  });
});
