# from project.helper.MyDb import MyDb
# from project.appComponents import apc
from .Auth import Auth
class AuthGroup(Auth):
	name = None
	desc = None
	created = None
	updated = None
	def __init__(self,name = None):
		self.name = name
	
	# def populate(self,dt):
	# 	self.name = dt["name"]
	# 	self.desc = dt["description"]
	# 	self.created = dt["created_at"]
	# 	self.updated = dt["updated_at"]