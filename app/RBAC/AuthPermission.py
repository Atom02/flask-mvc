# from project.helper.MyDb import MyDb
# from project.appComponents import apc
from .Auth import Auth
class AuthPermission(Auth):
	name = None
	type = None
	description = None
	group = None
	rule = None
	data = None
	created = None
	updated = None
	def __init__(self,name = None):
		self.name = name

	# def populate(self,dt):
	# 	self.name = dt["name"]
	# 	self.type = dt["type"]
	# 	self.desc = dt["description"]
	# 	self.desc = dt["group"]
	# 	self.rule = dt["rule_name"]
	# 	self.data = dt["data"]
	# 	self.created = dt["created_at"]
	# 	self.updated = dt["updated_at"]
	
