
import sys
sys.path.append('..')

from pycdm.dataset import Dataset
from pycdm.group import Group
from pycdm.variable import Dimension, Variable
from pycdm.field import Field

import netCDF4
import numpy
import copy



class netCDF4Variable(Variable):
	"""
	A subclass of the CDM Variable class that implements netcdf4 variable access
	"""
	
	def __init__(self, name, group, **kwargs):
		"""
		Creates a new netCDF4Variable instance by creating a basic variable instance and adding in the netCDF4 varobj instance
		"""
		super(netCDF4Variable, self).__init__(name, group, **kwargs)
		self.data = group.dataset.ncfile.variables[name]
	
	def __getitem__(self, slice):
		"""
		Implements the get item array slicing method
		
		>>> ds = netCDF4Dataset('../testdata/gfs.nc')
		>>> print ds.root.variables['latitude'][:2]
		[-89.84351531 -89.64079823]
		"""
		
		return self.data[slice]
		

class netCDF4Dataset(Dataset):
	"""
	A subclass of the CDM Dataset class that implements netcdf4 data storage format
	"""
	
	def __init__(self, location):
		"""
		Creates a new netCDFDataset instance by trying to open the file at location and building the CDM Dataset
		structure
		
		>>> ds = netCDF4Dataset('../testdata/gfs.nc')
		>>> print ds.root.dimensions
		[<CDM Dimension: latitude (880)>, <CDM Dimension: longitude (1760)>, <CDM Dimension: time (1)>]
		>>> print ds.root.variables['latitude']
		<CDM netCDF4Variable: latitude>
		>>> print ds.root.variables['TMAX_2maboveground'].dimensions
		[<CDM Dimension: time (1)>, <CDM Dimension: latitude (880)>, <CDM Dimension: longitude (1760)>]
		>>> print ds.root.attributes
		OrderedDict([(u'Conventions', u'COARDS'), (u'History', u'created by wgrib2'), (u'GRIB2_grid_template', 40)])
		>>> print ds.root.variables['latitude'].attributes
		OrderedDict([(u'units', u'degrees_north'), (u'long_name', u'latitude')])
		
		We can also use the group method coordinateVariables to get a list of coordinate variables from a group
		
		>>> print ds.root.coordinateVariables
		[<CDM netCDF4Variable: latitude>, <CDM netCDF4Variable: longitude>, <CDM netCDF4Variable: time>]
				
		>>> field = Field(ds.root.variables['TMAX_2maboveground'])
		>>> print field
		<CDM Field: [<CDM netCDF4Variable: time>, <CDM netCDF4Variable: latitude>, <CDM netCDF4Variable: longitude>]
		
		>>> print field.coordinates((0,440,1000))
		(1332892800.0, 0.10221463428702571, 204.5451961341671)
		
		"""
		
		# Call the super constructor
		super(netCDF4Dataset, self).__init__(location)
		
		# Open the NetCDF4 file
		self.ncfile = netCDF4.Dataset(self.location, 'r')
		
		# Creat the global attributes dictionary
		attributes = copy.deepcopy(self.ncfile.__dict__)
		
		# Create the dimensions list
		dimensions = [Dimension(name, len(dimobj)) for name, dimobj in self.ncfile.dimensions.items()]
		
		# Create the group
		self.root = Group(name='', dataset=self, attributes=attributes, dimensions=dimensions)

		# Create the variables
		variables = {}
		for varname, varobj in self.ncfile.variables.items():
			# Create the dimensions list
			vardims = [unicode(name) for name in varobj.dimensions]
			varattrs = copy.copy(varobj.__dict__)
			variables[varname] = netCDF4Variable(varname, group=self.root, dimensions=vardims, attributes=varattrs)
			
		self.root.variables = variables
		
	
		
		
	
