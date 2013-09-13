"""
An experiment to try and break the coordinate system functionality out of the Field class
"""


from variable import Variable

cf_dimensions = {'degree_east': 'longitude',
'degree east': 'longitude',
'degrees_east': 'longitude',
'degree_north': 'latitude',
'degrees_north': 'latitude',
'degree north': 'latitude'}

def cf_units2coordinates(units):
	
	# For spatial coordinates
	if units in cf_dimensions:
		return cf_dimensions[units]
	
	# Time coordinates
	try:
		netCDF4.num2date(0,units)
	except:
		return None
	
	return 'time'

class CoordSystem(object):
	"""
	Encapsulates a coordinate system.  Constructor can take a Variable instance and attempt to 
	auto construct the coordinate system parameters.
	"""
	
	def __init__(self, variable=None, coordsystem=None):
		"""
		Takes either a Variable instance or a coordsystem dict (produced by another CoordSystem instance)
		In the case of a variable instance, interogate the variable and auxilary variables in the parent
		group in order to construct the coordsystem parameters
		
		Coordinate systems can be of types: ['cartesian', 'discrete']
		
		Cartesian coordinate systems have an x-dimension and a y-dimension whereas discrete systems only
		have an id-dimension as an index into the grid positions.
		"""
		
		# If we have a variable instance
		if variable and type(variable) == Variable:
			
			# Keep a handle on the associated variable
			self.variable = variable
			
			# Initialise dimensions
			x_dimension = None
			y_dimension = None
			z_dimension = None
			t_dimension = None
			id_dimension = None
			
			# Keep track of variable dimensions we have mapped
			mapped = []

			# First just step through the variables dimensions
			for dimension in self.variable.dimensions:
				
				# See if the dimension name is also a variable name
				if dimension.name in self.variable.group.variables:
					
					# Grab the coordinate variable
					coordinate_variable = self.variable.group.variables[dimension.name]
					
					# Try and convert the variable into a CF coordinate
					cf_coordinate = cf_units2coordinates(coordinate_variable.get_attribute('units'))
					
					# Get the axis attribute
					axis = coordinate_variable.get_attribute('axis')
					
					# Now, if we have a cf_coordinate we can add this variable to the coordinate system
					# and mark it as mapped
					if cf_coordinate:
						self.coordsystem[cf_coordinate] = {'variable':coordinate_variable.name, 'map':[self.variable.dimensions.index(dimension)]}
						mapped.append(self.variable.dimensions.index(dimension))
						
					# We can also use cf_coordinates or axis attributes to figure out cartesian axis
					if cf_coordinate == 'latitude' or axis == 'Y':
						y_dimension = self.variable.dimensions.index(dimension)
					if cf_coordinate == 'longitude' or axis == 'X':
						x_dimension = self.variable.dimensions.index(dimension)
					if cf_coordinate == 'vertical' or axis == 'Z':
						z_dimension = self.variable.dimensions.index(dimension)
					if cf_coordinate == 'time' or axis == 'T':
						t_dimension = self.variable.dimensions.index(dimension)
	
			# Check how we are doing, have we mapped all dimensions?
			if len(mapped) < len(self.variable.dimensions):
				
				# Check for a coordinates attribute
				if self.variable.get_attribute('coordinates'):
						
					self.coordinates_names = self.variable.get_attribute('coordinates').split()
								
					# Find each associated variable
					for varname in self.coordinates_names:
									
						# See if we can find the corresponding variable
						if varname in self.variable.group.variables.keys():

							# Grab the coordinate variable
							coordinate_variable = self.variable.group.variables[varname]
							
							# Try and convert the variable into a CF coordinate
							cf_coordinate = cf_units2coordinates(coordinate_variable.get_attribute('units'))
							
							# Get the axis attribute
							axis = coordinate_variable.get_attribute('axis')

							# If we have a cf_coordinate we can create the mapping
							if cf_coordinate:

								# Create the coordinates_mapping entry but with an empty map for now
								self.coordinates_mapping[cf_coordinate] = {'variable':name, 'map':[], 'coordinates': self.coordinates_names}
								
								# Add each coordinates variable dimension to the mappable list and generate the map
								for dimension in self.variable.group.variables[varname].dimensions:
									self.coordinates_mapping[coordinate_name]['map'].append(self.variable.dimensions.index(dimension))
								
									if not dimension in mapped:
										mapped.append(dimension)

			# By now we should have mapped all the dimensions, we can now figure out what time of coordinate system we have
			
			# If we have x_dimension and y_dimension then we have a cartesian system
			if x_dimension and y_dimension:
				self.type = 'cartesian'
			
			
			# If the map for latitude and longitude is of length one and the same value then we can mark this as the id_dimension
			if self.coordinates_mapping['latitude']['map'] == self.coordinates_mapping['longitude']['map']:
				if len(self.coordinates_mapping['latitude']['map']) == 1:
					self.id_dimension = self.coordinates_mapping['latitude']['map'][0]
						
				
