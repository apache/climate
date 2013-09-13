
class CDMError(Exception):
	
	def __init__(self, message):
		self.message = message
		
	def __str__(self):
		return repr(self.message)


from dataset import Dataset
from variable import Dimension, Variable
from field import Field

from handlers import *

