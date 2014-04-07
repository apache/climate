
'''
 The scripts for processing MERG raw data
 #******************************************************************
 '''

import fileinput
import glob
import os
import re
import string
import subprocess
import sys

#----------------------- GLOBAL VARIABLES --------------------------
# --------------------- User defined variables ---------------------
LATMIN = '-5.0'         #min latitude; -ve values in the SH e.g. 5S = -5
LATMAX = '20.0'            #max latitude; -ve values in the SH e.g. 5S = -5
LONMIN = '-30.0'        #min longitude; -ve values in the WH e.g. 59.8W = -59.8
LONMAX = '30.0'            #min longitude; -ve values in the WH e.g. 59.8W = -59.8
T_BB_MAX = '250'           #warmest temp to allow in K
T_BB_MIN = '180'                        #coolest temp to allow in K
#------------------- End user defined Variables -------------------

#------------------------ End GLOBAL VARS -------------------------

def preprocessingMERG(MERGdirname):
    '''
    Purpose::
        Utility script for unzipping and converting the merg*.Z files from Mirador to
        NETCDF format. The files end up in a folder called mergNETCDF in the directory
        where the raw MERG data is
        NOTE: VERY RAW AND DIRTY

    Input::
        Directory to the location of the raw MERG files, preferably zipped

    Output::
       none

    Assumptions::
       1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
         have been installed on the system and the user can access
       2 User can write files in location where script is being called
       3 the files havent been unzipped
    '''

    os.chdir((MERGdirname+'/'))
    imgFilename = ''

    #Just incase the X11 server is giving problems
    subprocess.call('export DISPLAY=:0.0', shell=True)

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

        #TODO: must be something more pythonic!

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

        #generate the lats4D command for GrADS
        lats4D = 'lats4d -v -q -lat ' + LATMIN +' ' + LATMAX + ' ' + '-lon ' + LONMIN + ' ' + LONMAX + ' -time '+hr+'Z'+day+mth+yy + ' -func @+75 ' + '-i merg.ctl' + ' -o ' + fname

        gradscmd = 'grads -lbc ' + '\'' +lats4D + '\''
        #run grads and lats4d command
        subprocess.call(gradscmd, shell=True)

        #----- Generate GrADS images--------------
        imgFilename = hr+'Z'+day+mth+yy+'.gif'
        tempMaskedImages(imgFilename)
        #-------End Generate GrADS images ---------
        
        #remove the raw data file to save some resources
        rmCmd= "rm " + fname
        subprocess.call(rmCmd, shell=True)

    #when all the files have been converted, mv the netcdf files
    subprocess.call('mkdir mergNETCDF', shell=True)
    subprocess.call('mv *.nc mergNETCDF', shell=True)
    #mv all images
    subprocess.call('mkdir mergImgs', shell=True)
    subprocess.call('mv *.gif mergImgs', shell=True)

    return

#******************************************************************
def tempMaskedImages(imgFilename):
    '''
    Purpose:: To generate temperature-masked images for a first pass verification

    Input::
        filename for the gif file

    Output::
        None - gif images for each file of IR temperature < T_BB_MAX are generated in folder called mergImgs

    Assumptions::
       Same as for preprocessingMERG
       1 GrADS (http://www.iges.org/grads/gadoc/) and lats4D (http://opengrads.org/doc/scripts/lats4d/)
         have been installed on the system and the user can access
       2 User can write files in location where script is being called
       3 the files havent been unzipped
    '''

    subprocess.call('rm tempMaskedImages.gs', shell=True)
    subprocess.call('touch tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'open merg.ctl''\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set mpdset hires''\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set lat ' +LATMIN + ' ' +LATMAX +'\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set lon ' +LONMIN + ' ' +LONMAX +'\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set cint 10''\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set cmax '+T_BB_MAX +'\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'set cmin '+T_BB_MIN +'\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'d ch4+75''\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'draw title Masked Temp @ '+imgFilename +'\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'printim '+imgFilename +' x1000 y800''\'" >> tempMaskedImages.gs', shell=True)
    subprocess.call('echo "''\'quit''\'" >> tempMaskedImages.gs', shell=True)
    gradscmd = 'grads -blc ' + '\'run tempMaskedImages.gs''\''
    subprocess.call(gradscmd, shell=True)
    return

#******************************************************************
