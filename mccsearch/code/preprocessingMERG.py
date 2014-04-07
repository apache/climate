'''
#preprocessing for MERG data
# unzips files and generates the NETCDF files using GrADS lats4D
# http://opengrads.org/doc/scripts/lats4d/
# This script requires the merg_template.ctl resides with the folder 
# TODO: generate this file
# Kim Whitehall
# Last updated: June 4th 2013
'''
import subprocess
import fileinput
import json
import os
import glob
import re
import sys


def preprocessing_merg():
          '''
     Purpose::
         Utility script for unzipping and converting the merg*.Z files from Mirador to 
         NETCDF format
         NOTE: VERY RAW AND DIRTY 
     Input::
         none
          
     Output::
        none

     Assumptions::
        1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
          have been installed on the system and the user can access 
        2 User can write files in location where script is being called
        3 the files havent been unzipped     
     '''
     os.chdir("/Users/whitehal/Documents/kimSum2013/mergData1/")
     searchExpDset = "DSET "
     searchExpTdef = "TDEF "
     #for files in glob.glob("*-pixel"):
     for files in glob.glob("*.Z"):
          fname = os.path.splitext(files)[0]
          
          #unzip it
          bash_cmd = 'gunzip ' + files
          subprocess.call(bash_cmd, shell=True)
         
          #determine the time from the filename
          ftime = re.search('\_(.*)\_',fname).group(1)
          
          yy = ftime[0:4]
          mm = ftime[4:6]
          day = ftime[6:8]
          hr = ftime [8:10]
          

          if mm=='01':
               mth = 'Jan'
          if mm == '02':
               mth = 'Feb'
          if mm == '03':
               mth = 'Mar'
          if mm == '04':
               mth = 'Apr'
          if mm == '05':
               mth = 'May'
          if mm == '06':
               mth = 'Jun'
          if mm == '07':
               mth = 'Jul'
          if mm == '08':
               mth = 'Aug'
          if mm == '09':
               mth = 'Sep'
          if mm == '10':
               mth = 'Oct'
          if mm == '11':
               mth = 'Nov'
          if mm == '12':
               mth = 'Dec'


          subprocess.call('rm merg.ctl', shell=True)
          subprocess.call('touch merg.ctl', shell=True)
          replaceExpDset = 'echo DSET ' + fname +' >> merg.ctl'
          replaceExpTdef = 'echo TDEF 99999 LINEAR '+hr+'z'+day+mth+yy +' 30mn' +' >> merg.ctl'
          subprocess.call(replaceExpDset, shell=True) 
          subprocess.call('echo "OPTIONS yrev little_endian template" >> merg.ctl', shell=True)
          subprocess.call('echo "UNDEF  330" >> merg.ctl', shell=True)
          subprocess.call('echo "TITLE  globally merged IR data" >> merg.ctl', shell=True)
          subprocess.call('echo "XDEF 9896 LINEAR   0.0182 0.036378335" >> merg.ctl', shell=True)
          subprocess.call('echo "YDEF 3298 LINEAR   -59.982 0.036383683" >> merg.ctl', shell=True)
          subprocess.call('echo "ZDEF   01 LEVELS 1" >> merg.ctl', shell=True)
          subprocess.call(replaceExpTdef, shell=True)
          subprocess.call('echo "VARS 1" >> merg.ctl', shell=True)
          subprocess.call('echo "ch4  1  -1,40,1,-1 IR BT  (add  "75" to this value)" >> merg.ctl', shell=True)
          subprocess.call('echo "ENDVARS" >> merg.ctl', shell=True)



          # #cp template merg.ctl
          # subprocess.call('cp -f merg_template.ctl merg.ctl', shell=True)
         
          # #edit merg.ctl dset line to contain filename by running file
          # #http://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
          # replaceExpDset = 'DSET ' + fname
          # replaceExpTdef = 'TDEF 99999 LINEAR '+hr+'z'+day+mth+yy +' 30mn'
          # for line in fileinput.input("merg.ctl", inplace=True):
          #      if searchExpDset in line:
          #           line = line.replace(searchExpDset, replaceExpDset)
          #      if searchExpTdef in line:
          #           line = line.replace(searchExpTdef, replaceExpTdef)
          #      sys.stdout.write(line) 

          #lats4d cmd
          lats4D = 'lats4d -v -q -lat -5 40 -lon -90 60 -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname
          
          gradscmd = 'grads -blc ' + '\'' +lats4D + '\''
          #run grads and lats4d command
          subprocess.call(gradscmd, shell=True)

     #when all the files have benn converted, mv the netcdf files
     subprocess.call('mkdir mergNETCDF', shell=True)
     subprocess.call('mv *.nc mergNETCDF', shell=True)
     return