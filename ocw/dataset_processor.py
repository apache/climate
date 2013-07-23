#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import numpy as np
import scipy.interpolate
import scipy.ndimage

def temporal_rebin(Dataset, temporal_resolution):
    """ Rebin a Dataset to a new temporal resolution
    
    :param Dataset: Dataset object that need temporal regridding applied
    :type Dataset: Open Climate Workbench Dataset Object
    :param temporal_resolution: The new temporal bin size
    :type temporal_resolution: Python datetime.timedelta object
    
    :returns: A new temporally rebinned Dataset
    :rtype: Open Climate Workbench Dataset Object
    """
    # This will call down into the _congrid() function within this module
    # after using the temporal_resolution to determine the new number of time
    # bins to use in the resulting output Dataset.  Only the time axis of the 
    # Dataset will be changed 
    pass

def spatial_regrid(Dataset, lon_resolution, lat_resolution):
    """ Regrid a Dataset using the new latitude and longitude resolutions
    
    :param Dataset: Dataset object that need temporal regridding applied
    :type Dataset: Open Climate Workbench Dataset Object
    :param lon_resolution: Longitude resolution in degrees
    :type lon_resolution: float
    :param lat_resolution: Latitude resolution in degrees
    :type lat_resolution: float
    
    :returns: A new spatially regridded Dataset
    :rtype: Open Climate Workbench Dataset Object
    """
    # This will call down to the _congrid() function and the lat and lon 
    # axis will be adjusted with the time axis being held constant
    pass

def ensemble(datasets):
    pass

def _congrid(a, newdims, method='linear', centre=False, minusone=False):
    '''
    This function is from http://wiki.scipy.org/Cookbook/Rebinning - Example 3
    It has been refactored and changed a bit, but the original functionality
    has been preserved.
    
    Arbitrary resampling of source array to new dimension sizes.
    Currently only supports maintaining the same number of dimensions.
    To use 1-D arrays, first promote them to shape (x,1).
    
    Uses the same parameters and creates the same co-ordinate lookup points
    as IDL''s congrid routine, which apparently originally came from a VAX/VMS
    routine of the same name.

    method:
    neighbour - closest value from original data
    nearest and linear - uses n x 1-D interpolations using
                         scipy.interpolate.interp1d
    (see Numerical Recipes for validity of use of n 1-D interpolations)
    spline - uses ndimage.map_coordinates

    centre:
    True - interpolation points are at the centres of the bins
    False - points are at the front edge of the bin

    minusone:
    For example- inarray.shape = (i,j) & new dimensions = (x,y)
    False - inarray is resampled by factors of (i/x) * (j/y)
    True - inarray is resampled by(i-1)/(x-1) * (j-1)/(y-1)
    This prevents extrapolation one element beyond bounds of input array.
    '''
    if not a.dtype in [np.float64, np.float32]:
        a = np.cast[float](a)

    # this will merely take the True/False input and convert it to an array(1) or array(0)
    m1 = np.cast[int](minusone)
    # this also casts the True False input into a floating point number of 0.5 or 0.0
    ofs = np.cast[int](centre) * 0.5

    old = np.array( a.shape )
    ndims = len( a.shape )
    if len( newdims ) != ndims:
        print "[congrid] dimensions error. " \
              "This routine currently only supports " \
              "rebinning to the same number of dimensions."
        return None
    newdims = np.asarray( newdims, dtype=float )
    dimlist = []

    if method == 'neighbour':
        newa = _congrid_neighbor(a, newdims, m1, ofs)
        """
        for i in range( ndims ):
            base = np.indices(newdims)[i]
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        cd = np.array( dimlist ).round().astype(int)
        newa = a[list( cd )]
        return newa
        """

    elif method in ['nearest','linear']:
        # calculate new dims
        for i in range( ndims ):
            base = np.arange( newdims[i] )
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        # specify old dims
        olddims = [np.arange(i, dtype = np.float) for i in list( a.shape )]

        # first interpolation - for ndims = any
        mint = scipy.interpolate.interp1d( olddims[-1], a, kind=method )
        newa = mint( dimlist[-1] )

        trorder = [ndims - 1] + range( ndims - 1 )
        for i in range( ndims - 2, -1, -1 ):
            newa = newa.transpose( trorder )

            mint = scipy.interpolate.interp1d( olddims[i], newa, kind=method )
            newa = mint( dimlist[i] )

        if ndims > 1:
            # need one more transpose to return to original dimensions
            newa = newa.transpose( trorder )

        return newa
    elif method in ['spline']:
        oslices = [ slice(0,j) for j in old ]
        oldcoords = np.ogrid[oslices]
        nslices = [ slice(0,j) for j in list(newdims) ]
        newcoords = np.mgrid[nslices]

        newcoords_dims = range(np.rank(newcoords))
        #make first index last
        newcoords_dims.append(newcoords_dims.pop(0))
        newcoords_tr = newcoords.transpose(newcoords_dims)
        # makes a view that affects newcoords

        newcoords_tr += ofs

        deltas = (np.asarray(old) - m1) / (newdims - m1)
        newcoords_tr *= deltas

        newcoords_tr -= ofs

        newa = scipy.ndimage.map_coordinates(a, newcoords)
        return newa
    else:
        print "Congrid error: Unrecognized interpolation type.\n", \
              "Currently only \'neighbour\', \'nearest\',\'linear\',", \
              "and \'spline\' are supported."
        return None

def _congrid_neighbor(values, new_dims, minus_one, offset):
    """ Use the nearest neighbor to create a new array
    
    :param values: Array of values that need to be interpolated
    :type values: Numpy ndarray
    :param new_dims: Longitude resolution in degrees
    :type new_dims: float
    :param lat_resolution: Latitude resolution in degrees
    :type lat_resolution: float
    
    :returns: A new spatially regridded Dataset
    :rtype: Open Climate Workbench Dataset Object
    """
    ndims = len( values.shape )
    dimlist = []
    old_dims = np.array( values.shape )
    for i in range( ndims ):
        base = np.indices(new_dims)[i]
        dimlist.append( (old_dims[i] - minus_one) / (new_dims[i] - minus_one) \
                        * (base + offset) - offset )
    cd = np.array( dimlist ).round().astype(int)
    new_values = a[list( cd )]
    return new_values    