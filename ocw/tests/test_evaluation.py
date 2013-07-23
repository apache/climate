# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''Unit tests for the Evaluation.py module'''

import unittest
from dataset import Dataset
from evaluation import Evaluation

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.eval = Evaluation()

    def test_init(self):
        self.assertEquals(self.eval.ref_dataset, None)
        self.assertEquals(self.eval.target_datasets, [])
        self.assertEquals(self.eval.metrics, [])

if __name__  == '__main__':
    unittest.main()
