class Dataset(object):
	"""A generic Dataset class that represents an abstract dataset.  This class is subclassed in order to
	implement different storage handlers.
	
	Storage handlers should overload the init method in order to construct a Dataset object.  The open method will
	search for the first subclass that can open the provided location and return a new Dataset instance if successful.
	
	"""
	
	def __init__(self, location=None):
		"""
		Create a new generic dataset instance that just hold the location string if provided and sets
		the root group to None
		>>> ds = Dataset()
		>>> print ds
		<CDM Dataset: None>
		>>> print ds.root
		None
		"""

		self.location = location
		self.root = None
		self.attributes = {}
				
						
	@classmethod
	def open(cls, location):
		"""
		Class method that finds an appropriate Dataset subclass to handle the resource identified by
		location, constructs an instance of this subclass and returns it.  Returns None if no handler
		subclass can be found.
		>>> print Dataset.open(None)
		<CDM Dataset: None>
		>>> print Dataset.open('doesnotexist')
		None
		"""
		
		# If we have a location parameter, try to find a handler
		if (location):
			dataset = None	
			for handler in cls.__subclasses__():
				try:
					dataset = handler(location)
				except:
					pass
				else:
					break
			return dataset
		
		# Else return a generic dataset instance
		else:
			return Dataset()

	def close(self):
		"""
		Method to be implemented by format handling subclasses as appropriate
		"""
		
		pass
		

	def getRootGroup(self):
		"""
		To be overloaded as needed by handler subclass but otherwise just returns the
		instance root variable
		>>> ds = Dataset()
		>>> print ds.getRootGroup()
		None
		"""
		
		return self.root
		
		
	def __repr__(self):
		return "<CDM %s: %s>" % (self.__class__.__name__, self.location)

	def __unicode__(self):
		return self.__repr__()
