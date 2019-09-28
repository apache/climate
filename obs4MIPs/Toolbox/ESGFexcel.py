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

from __future__ import print_function

import pdb
import xlrd
import shutil
import os,sys
from numpy import arange
from Toolbox.CMORresources import CMORAttributes

#  ********************************************************************
#         ESGFexcel()
#
#  ********************************************************************
class ESGFexcel:
    '''
    Create dictionary based on a file using key=value standard from Excel
    Sheet resource Key is in Column A, Value is in Column B.     
    '''
    def __init__(self,excelFile):
        '''
        '''
        self.xcl = excelFile
        if( os.path.isfile(self.xcl) ):
                wb=xlrd.open_workbook(self.xcl)
        else:
           print("****** Could not find {} file ****".format(self.xcl))
           print("****** Please check excel file name ****")
           raise NameError(self.xcl)

        sheet=wb.sheet_by_name('Resources')

        for i in  arange(sheet.nrows-1) + 1: 
            key = sheet.row(i)[0]
            value  = sheet.row(i)[1]

        self.resources = dict( [( key, value, ) 
                               for( key, value ) in 
                               [ (sheet.row(i)[0].value, str(sheet.row(i)[1].value)) 
                                 for i in  arange(sheet.nrows-1) + 1] ] )
        pdb.set_trace()
        self.ReadXCL()
        print(self.resources.keys())

    def ReadXCL(self):
        '''
        Read Excel Table and fill rc variable related field.
        '''
        try:
           import xlrd
        except:
           print("****** Could not find xlrd Python Package ****")
           print("****** Please install xlrd package to read excel files ****")

        if( os.path.isfile(self.xcl) ):
                wb=xlrd.open_workbook(self.xcl)
        else:
           print("****** Could not find {} file ****".format(self.xcl))
           print("****** Please check excel file name ****")
           raise NameError(self.xcl)

        sheet=wb.sheet_by_name('Variables')

        self.resources['cmor_var']    = [ sheet.row( i )[ 0 ].value.\
                                          encode('ascii','ignore') \
                                          for i in arange(sheet.nrows-2) + 2 ]

        self.resources['original_var'] = [ sheet.row( i )[ 1 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        self.resources['original_units']=[ sheet.row( i )[ 2 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        self.resources['level']         =[ sheet.row( i )[ 3 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2]

        self.resources['equation']     =[ sheet.row( i )[ 6 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        # -----------------------------------------------------------------
        # Make sure it is a string. The main program will call eval on it.
        # -----------------------------------------------------------------
        self.resources['cmor_var']       = str(self.resources['cmor_var'] )
        self.resources['original_var']   = str(self.resources['original_var'])
        self.resources['original_units'] =str(self.resources['original_units'])
        self.resources['equation']       =str(self.resources['equation'])
        self.resources['level']          =str(self.resources['level'])
        return 1

    def __getitem__(self,key):
        '''
        Retreive item from resource dictionary
        '''
        return self.resources[key]

    def __setitem__(self,key,value):
        '''
        '''
        self.resources[key]=value

    def __delete__(self,key):
        '''
        '''
        del self.resources[key]


