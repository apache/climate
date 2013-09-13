from dataset import Dataset

class Group(object):
	
	def __init__(self, name, dataset, parent=None, dimensions=[], attributes={}, variables={}):
		"""
		Creates a new group object with a given name and within the given dataset.  An empty name
		string marks the group as a root group within the dataset. Can also assign this group a 
		position in a group hierachy by specifying its parent group which must be another Group 
		instance assigned to the same dataset
		>>> ds = Dataset()
		>>> group = Group('', ds)
		>>> print group.dataset
		<CDM Dataset: None>
		>>> print ds.root
		<CDM Group: [root]>
		>>> child1 = Group('child1', ds, parent=group)
		>>> child2 = Group('child2', ds, parent=group)
		>>> print child1.parent
		<CDM Group: [root]>
		>>> print child2.parent
		<CDM Group: [root]>
		>>> print group.children
		[<CDM Group: child1>, <CDM Group: child2>]
		"""
		
		self.name = name
		self.dataset = dataset
		self.parent = parent
		self.variables = variables
		self.attributes = attributes
		self.dimensions = dimensions
		self.children = []
		
		# If there is no parent then this must be a root group which must have an empty 
		# string as the name
		if (not parent):
			dataset.root = self
			self.name = '[root]'
		
		# Add group into a datasets group hierachy
		elif (type(parent) == Group and parent.dataset == dataset):
			self.parent = parent
			parent.children.append(self)
			
	def __repr__(self):
		return "<CDM %s: %s>" % (self.__class__.__name__, self.name)
