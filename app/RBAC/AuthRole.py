# from project.helper.MyDb import MyDb
# from project.appComponents import apc
from .Auth import Auth


class AuthRole(Auth):
	name = None
	type = None
	description = None
	group = None
	rule = None
	data = None
	created = None
	updated = None
	rule_name = None

	def __init__(self, name = None):
		self.name = name

	# def populate(self,dt):
	# 	self.name = dt["name"]
	# 	self.type = dt["type"]
	# 	self.desc = dt["description"]
	# 	self.rule = dt["rule_name"]
	# 	self.data = dt["data"]
	# 	self.craeted = dt["created_at"]
	# 	self.updated = dt["updated_at"]

