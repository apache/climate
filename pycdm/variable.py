
from dataset import Dataset
from group import Group
from field import Field

import numpy

class Dimension(object):
	"""
	A Dimension is used to define the array shape of a Variable. It may be shared among Variables, which 
	provides a simple yet powerful way of associating Variables. When a Dimension is shared, it has a 
	unique name within the Group. If unlimited, a Dimension's length may increase. If variableLength, then 
	the actual length is data dependent, and can only be found by reading the data. A variableLength 
	Dimension cannot be shared or unlimited.
	"""
	
	def __init__(self, name, length, unlimited=False, shared=True, variableLength=False):
		"""
		Create a dimenion instance with a given name and length
		>>> d1 = Dimension('latitude', 90)
		>>> print d1
		<CDM Dimension: latitude (90)>
		>>> print d1.isUnlimited
		False
		>>> print d1.isShared
		True
		>>> print d1.isVariableLength
		False
		"""
		
		self.name = name
		self.length = length
		self._unlimited = unlimited
		self._shared = shared
		self._variableLength = variableLength
		
		
	@property
	def isUnlimited(self):
		return self._unlimited
	
	@property
	def isShared(self):
		return self._shared
		
	@property
	def isVariableLength(self):
		return self._variableLength
		
	def __repr__(self):
		return "<CDM %s: %s (%d)>" % (self.__class__.__name__, self.name, self.length)


class Variable(object):
	"""
	A Variable is a container for data. It has a DataType, a set of Dimensions that define its array 
	shape, and optionally a set of Attributes. Any shared Dimension it uses must be in the same Group 
	or a parent Group.
	"""
	
	def __init__(self, name, group, dimensions=[], attributes={}, dtype=numpy.float32, data=None):
		"""
		Create a variable instance with given name and group and optional ordered list of dimensions, 
		attributes dictionary and alternative data type (dtype).  dtype defaults to numpy.float32.
		
		If a dimension is a dimension instance then if it is shared it will be added to the groups dimension list
		and the local reference will be replace by the dimension name.  If it is not shared the local reference will
		remain the dimension instance.
		
		If a dimension is a string then a dimension by that name will be searched for in the groups dimension list.  Failure
		to find a match will throw an exception.
		
		>>> ds = Dataset()
		>>> group = Group('', ds)
		>>> lat = Dimension('latitude', 90)
		>>> lon = Dimension('longitude', 180)
		>>> var = Variable('tmax', group, dimensions=[lat, lon], attributes={'units': 'degrees K'})
		>>> print var
		<CDM Variable: tmax>
		>>> print var.attributes
		{'units': 'degrees K'}
		>>> print var.dimensions
		[<CDM Dimension: latitude (90)>, <CDM Dimension: longitude (180)>]
		>>> var2 = Variable('tmax', group, dimensions=['latitude', 'longitude'], attributes={'units': 'degrees K'})
		
		Dimensions can also be specified by name if they already exist in the group
		
		>>> print var2.dimensions
		[<CDM Dimension: latitude (90)>, <CDM Dimension: longitude (180)>]
		
		>>> print var.shape
		(90, 180)
		"""
		
		self.name = name
		self.group = group
		self.attributes = attributes
		self.dtype = dtype
		self._dimensions = []
		self._data = data
		
		# Process dimensions
		for dimension in dimensions:
			# If dimension is a Dimension instance
			if isinstance(dimension, Dimension):
				
				# If it is shared
				if dimension.isShared:
					
					# Try to add it to the groups dimension list				
					if not dimension in self.group.dimensions:
						self.group.dimensions.append(dimension)
				
					# Replace the local reference by its name
					self._dimensions.append(dimension.name)
				
				# If its not shared
				else:
					self._dimensions.append(dimension)
				
			# If the dimension is a string
			elif isinstance(dimension, unicode) or isinstance(dimension, str):
				# If a dimension of this name is in the groups dimension list then we're okay
				if dimension in map(lambda d: d.name, self.group.dimensions):
					self._dimensions.append(dimension)


	@property
	def dimensions(self):
		
		result = []
		
		for dimension in self._dimensions:
			# If its a string then we need to find the instance in the groups dimension list
			if isinstance(dimension, unicode) or isinstance(dimension, str):
				
				# Try to find a dimension of this name
				found = False
				for group_dimension in self.group.dimensions:
					if group_dimension.name == dimension:
						result.append(group_dimension)
						found = True
						break
				
				# If we don't find it then throw an exception
				if not found:
					result.append(None)
								
			# If its a dimension instance then just append it
			elif isinstance(dimension, Dimension):
				result.append(dimension)
		
		return result
						
			
	@property	
	def shape(self):
		
		shape = tuple()
		for dimension in self.dimensions:
			shape = shape + (dimension.length, )
		return shape
		
	def __repr__(self):
		return "<CDM %s: %s>" % (self.__class__.__name__, self.name)
	
	def get_attribute(self, name):
		"""
		Return the value of the attribute with given name or None if such an attribute does
		not exist
		"""
		
		if self.attributes.has_key(name):
			return self.attributes[name]
		else:
			return None
	
	def getAttribute(self, name):
		"""
		Depreciated: use get_attribute 
		Return the value of the attribute with given name or None if such an attribute does
		not exist
		"""
		
		if self.attributes.has_key(name):
			return self.attributes[name]
		else:
			return None

	
	def __getitem__(self, slice):
		"""
		Returns a slice of the variables data array
		"""
		if self._data != None:
			return self._data[slice]
		else:
			return None



	def getSubset(self, **kwargs):
		
		print kwargs
		slices = []
		for i in range(0,len(self.shape())):
			slices.append(slice(None, None))
		
		print slices
		
		for key in kwargs:
						
			if (key in self.dimensions):
				index = self.dimensions.index(key)					
				
				if (key in self.group.variables):
					vals = self.group.variables[key][:]
					
					# For single values
					if (type(kwargs[key]) != tuple):
						start = end = kwargs[key]
						match = True
					# for tuples
					elif (type(kwargs[key]) == tuple):
						start = kwargs[key][0]
						end = kwargs[key][1]
					
					# Special case for time slices
					if (key == 'time'):
						units = self.group.variables['time'].attributes['units']
						calendar = self.group.variables['time'].attributes['calendar']
						print units
						
						start = netCDF4.date2num(start, units, calendar)
						end = netCDF4.date2num(end, units, calendar)
					
					index0 = numpy.searchsorted(vals, start, "left")
					index1 = numpy.searchsorted(vals, end, "left")

					print vals
					print key, start, end, vals[index0], vals[index1]
					
					
					slices[index] = slice(index0, index1)
					
		print slices
		

	def asField(self):
	
		return Field(self)

	def __add__(self, other):
		"""
		Overloads the addition operator by delegating to the underlying numpy array addition
		>>> import handlers.netcdf4 as netcdf4
		>>> import handlers.csag2 as csag2

		>>> ds = netcdf4.netCDF4Dataset('../testdata/gfs.subset.nc')
		>>> tmax = ds.root.variables['TMAX_2maboveground']
		>>> tmin = ds.root.variables['TMIN_2maboveground']
		>>> t = tmin+tmax
		>>> print t
		<CDM Variable: (TMIN_2maboveground+TMAX_2maboveground)>
		"""
		
		# We can only do this if the two variables have the same shape
		if (self.shape == other.shape):
			
			# We need to construct a name for this variable
			name = '(%s+%s)' % (self.name, other.name)
					
			# Create the new variable
			new_variable = Variable(name, self.group, dimensions=self.dimensions, attributes=self.attributes)

			# Then we do the operation
			new_variable._data = self[:] + other[:]
			
		else:
			
			raise CDMError("Cannot add variables of different shapes")
			
		return new_variable
			
	def __sub__(self, other):
		"""
		Overloads the subtraction operator by delegating to the underlying numpy array addition
		>>> import handlers.netcdf4 as netcdf4
		>>> import handlers.csag2 as csag2

		>>> ds = netcdf4.netCDF4Dataset('../testdata/gfs.subset.nc')
		>>> tmax = ds.root.variables['TMAX_2maboveground']
		>>> tmin = ds.root.variables['TMIN_2maboveground']
		>>> t = tmax-tmin
		>>> print t
		<CDM Variable: (TMAX_2maboveground-TMIN_2maboveground)>
		>>> print tmin[2,45,60], tmax[2,45,60], t[2,45,60]
		285.4 285.7 0.300018
		"""
		
		# We can only do this if the two variables have the same shape
		if (self.shape == other.shape):
			
			# We need to construct a name for this variable
			name = '(%s-%s)' % (self.name, other.name)
					
			# Create the new variable
			new_variable = Variable(name, self.group, dimensions=self.dimensions, attributes=self.attributes)

			# Then we do the operation
			
			new_variable._data = self[:] - other[:]
			
		else:
			
			raise CDMError("Cannot add variables of different shapes")
			
		return new_variable
			
