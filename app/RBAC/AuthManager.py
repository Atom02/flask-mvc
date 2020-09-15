from project import app,cache
from app.MyDb import MyDb
from project.appConfig import components as cp
from .Auth import Auth
from .BaseManager import BaseManager
from .AuthGroup import AuthGroup
from .AuthPermission import AuthPermission
from .AuthRole import AuthRole
from .AuthAssignment import AuthAssignment
from .AuthRule import AuthRule
# from werkzeug.contrib.cache import MemcachedCache
from phpserialize import serialize, unserialize
from pathlib import Path
from pydoc import locate
import importlib
import time
import pickle
import sys

class BaseClass():
	pass


class AuthManager(BaseManager):
	# sys.setrecursionlimit(15000)
	TYPE_ROLE = 1
	TYPE_PERMISSION = 2
	TYPE_GROUP = 3

	db = None
	__type = None
	__table = {
		"itemTable": "auth_item",
		"itemChildTable": "auth_item_child",
		"assignmentTable": "auth_assignment",
		"ruleTable": "auth_rule",
		"groupTable": "auth_group"
	}
	cache = None
	c = None
	# cacheKey = app.config['CACHE_KEY']
	cacheKey = "AUTHRBAC"
	item = None
	items = {}
	rules = {}
	parents = {}
	groups = {}
	__checkAccessAssignments = {}
	defaultRoles = []

	def __init__(self, db=None):
		# print ("Role Class Initated")
		z = self.__table.copy()
		z.update(cp["RBAC"])
		self.__table = z
		if db == None:
			raise ValueError("Where IS THE DB??")
		self.db = db
		# c = MemcachedCache(['localhost:11211'])
		# if c.get(self.cacheKey) is None:
		# 	if c.set(app.config['CACHE_KEY'], {}) is False:
		# 		raise RuntimeError("Unable To Set RBAC CACHE")
		# else:
		# 	self.cache = c.get(app.config['CACHE_KEY'])
		self.c = cache
		if self.c.get(self.cacheKey) == None:
			if self.c.set(self.cacheKey, {}) == False:
				raise RuntimeError("Unable To Set RBAC CACHE")
		
		# self.cache = self.c.get(self.cacheKey)
		# pass

	@staticmethod
	def __merge_two_dicts(x, y):
		z = x.copy()
		z.update(y)
		return z

	def checkAccess(self, userId, permissionName, params={}):
		if userId in self.__checkAccessAssignments:
			print("uidInCAA")
			assignments = self.__checkAccessAssignments[userId]
		else:
			print("uidNotInCAA")
			assignments = self.getAssignments(userId)
			print(assignments,bool(assignments))

		if self.hasNoAssignments(assignments) == True:
			return False

		self.loadFromCache()
		if bool(self.items) == (not False):
			print("Load FromCache")
			return self.__checkAccessFromCache(userId, permissionName, params, assignments)
		else:
			print("Load Recrusive")
			return self.__checkAccessRecursive(userId, permissionName, params, assignments)

	def __checkAccessFromCache(self, user, itemName, params, assignments):
		if itemName in self.items:
			return False
		item = self.items[itemName]
		if self.executeRule(user, item, params) == False:
			return False
		if itemName in assignments or itemName in self.defaultRoles:
			return True
		if bool(self.parents[itemName]) == (not False):
			for parent in self.parents[itemName]:
				if self.__checkAccessFromCache(user, itemName, params, assignments):
					return True

	def __checkAccessRecursive(self, user, itemName, params, assignments):
		item = self.__getItem(itemName)
		if item == None:
			return False
		if self.executeRule(user, item, params) == False:
			return False
		if itemName in assignments or itemName in self.defaultRoles:
			return True
		cur = self.db.getDb()
		q="""
			select parent from {itemChild} where child = %(itemName)s
		""".format(itemChild=self.__table["itemChildTable"])
		qp = {"itemName":itemName}
		# try:
		cur.execute(q,qp)
		# print(cur._last_executed)
		# except Exception as e:
		# 	print(cur._last_executed)
			# raise ValueError('IT IS ME.. dont wory')
		if cur.rowcount > 0:
			res = cur.fetchall()
			for row in res:
				if self.__checkAccessRecursive(user, row["parent"], params, assignments) == True:
					return True
		return False
	
	def __getItem(self, name=None):
		name = name.strip()
		if name == None:
			return None
		if name in self.items:
			return self.items[name]
		cur = self.db.getDb()
		q = """select * from {table} where name=%(name)s limit 1""".format(
			table=self.__table["itemTable"])
		cur.execute(q, {"name": name})
		if cur.rowcount == 0:
			return None
		res = cur.fetchone()
		return self.populateItem(res)

	def __getItems(self, itemType):
		cur = self.db.getDb()
		q = """select * from {table} where type=%(type)s""".format(
			table=self.__table["itemTable"])
		q = cur.execute(q, {"type": itemType})
		items = {}
		res = cur.fetchall()
		for row in res:
			items[row["name"]] = self.populateItem(row)
		return items
	
	def __getChildrenList(self):
		cur = self.db.getDb()
		q=""" select * from {table} """.format(table=self.__table["itemChildTable"])
		cur.execute(q)
		parents = {}
		res = cur.fetchall()
		for row in res:
			if not bool(row["parent"] in parents):
				parents[row["parent"]] = []
			parents[row["parent"]].append(row["child"])
		return parents
	
	def __getChildrenRecursive(self,name,childrenlist,result):
		if name in childrenlist:
			for child in childrenlist[name]:
				result[child] = True
				self.__getChildrenRecursive(child,childrenlist,result)
	
	def __addItem(self, item):
		stime = int(time.time())
		cur = self.db.getDb()
		# print(item.group)
		if isinstance(item.group, AuthGroup):
			item.group = item.group.name
		
		if issubclass(type(item.rule), AuthRule):
			item.rule = item.rule.name

		if item.created == None:
			item.created = stime
		if item.updated == None:
			item.updated = stime
		q = """
			insert into {table} (name,type,`group`,description,rule_name,data,created_at,updated_at)
			values (%(name)s,%(type)s,%(group)s,%(description)s,%(rule_name)s,%(data)s,%(created_at)s,%(updated_at)s)
		""".format(table=self.__table["itemTable"])
		qp = {"name": item.name, "type": item.type, "group": item.group,"rule_name":item.rule, "description": item.description, 
				"data": item.data, "created_at": item.created, "updated_at": item.updated}
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __addRule(self, rule):
		stime = int(time.time())
		cur = self.db.getDb()
		if rule.created == None:
			rule.created = stime
		if rule.updated == None:
			rule.updated = stime
		# print(rule.name)
		data = pickle.dumps(rule)
		q = """
			insert into {rule} (name,data,created_at,updated_at)
			values (%(name)s,%(data)s,%(created_at)s,%(updated_at)s)
		""".format(rule=self.__table["ruleTable"])
		qp = {"name": rule.name, "data": data,
			  "created_at": rule.created, "updated_at": rule.updated}
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __addGroup(self, object):
		group = object
		stime = int(time.time())
		cur = self.db.getDb()
		if(group.craeted == None):
			group.created = stime
		if(group.updated == None):
			group.updated = stime
		qp = {}
		qp["name"] = group.name
		qp["description"] = group.description
		qp["created_at"] = group.created
		qp["updated_at"] = group.updated
		q = """
		insert into {} values (%(name)s,%(description)s,%(created_at)s,%(updated_at)s)
		""".format(self.__table["groupTable"])
		cur.execute(q, qp)
		self.invalidateCache()

	def __removeItem(self, item):
		cur = self.db.getDb()
		qp = {"name": item.name}
		# q="""
		#     delete from {itemChild} where (parent = %(name)s or child = %(name)s)
		# """.format(itemChild=self.__table["itemChildTable"])
		# cur.execute(q,qp)
		# q="""
		#     delete from {assignment} where item_name = %(name)s
		# """.format(assignment=self.__table["assignmentTable"])
		# cur.execute(q,qp)
		q = """
			delete from {item} where name = %(name)s
		""".format(item=self.__table["itemTable"])
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __removeRule(self, rule):
		cur = self.db.getDb()
		qp = {"rule_name": item.rule_name}
		# q="""
		#     update {item} set rule_name = NULL where rule_name=%(rule_name)s
		# """.format(item=self.__table["itemTable"])
		# cur.execute(q,qp)
		q = """
			delete from {rule} where name = %(rule_name)s
		""".format(rule=self.__table["ruleTable"])
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __removeGroup(self, group):
		cur = self.db.getDb()
		qp = {"group": group.name}
		# uncomment for db not support cascade
		# q="""
		#     update {item} set group = NULL where group = %(group)s
		# """.format(item=self.__table["itemTable"])
		# cur.execute(q,qp)
		q = """
			delete from {group} where name = %(group)s
		""".format(group=self.__table["groupTable"])
		cur.execute(q, qp)

		q = """
			update {item} set group = NULL where group = %(group)s
		""".format(item=self.__table["itemTable"])
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __updateItem(self, name, item):
		# print("Update Item Child Called")
		stime = int(time.time())
		item.update = stime
		cur = self.db.getDb()
		q = """
			update {item} set 
				name = %(name)s,
				`group` = %(group)s,
				description = %(description)s,
				rule_name = %(rule_name)s, 
				data = %(data)s,
				updated_at = %(updated_at)s
			where 
				name = %(uname)s
		""".format(item=self.__table["itemTable"])
		qp = {
			"name": item.name,
			"group": item.group,
			"description": item.description,
			"rule_name": item.rule_name,
			"data": item.data,
			"updated_at": item.update,
			"uname": name}
		cur.execute(q, qp)
		# print(cur._last_executed)
		self.invalidateCache()
		return True

	def __updateRule(self, name, rule):
		# if ($rule->name !== $name && !$this->supportsCascadeUpdate()) {
		#     $this->db->createCommand()
		#         ->update($this->itemTable, ['rule_name' => $rule->name], ['rule_name' => $name])
		#         ->execute();
		# }
		stime = int(time.time())
		rule.update = stime
		cur = self.db.getDb()
		q = """
			update {rule} set name = %(name)s, data = %(data)s, updated_at = %(updated_at)s
			where name = %(uname)s
		""".format(rule=self.__table["ruleTable"])
		qp = {"name": rule.name, "data": rule.data,
			  "updated_at": rule.updated, "uname": name}
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def __updateGroup(self, name, group):
		stime = int(time.time())
		group.update = stime
		cur = self.db.getDb()
		q = """
			update {group} set name = %(name)s, description = %(description)s, updated_at = %(updated_at)s
			where uname = %(uname)s
		""".format(group=self.__table["groupTable"])
		qp = {"name": group.name, "description": group.description,
			  "updated_at": group.updated}
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def createRole(self, name):
		self.__type = self.TYPE_ROLE
		role = AuthRole(name)
		role.type = self.TYPE_ROLE
		return role

	def createPermission(self, name):
		self.__type = self.TYPE_PERMISSION
		permission = AuthPermission(name)
		permission.type = self.TYPE_PERMISSION
		return permission

	def createGroup(self, name):
		self.__type = self.TYPE_GROUP
		group = AuthGroup(name)		
		return group

	def add(self, object):
		if isinstance(object, AuthGroup):
			self.__addGroup(object)
		elif isinstance(object, AuthPermission):
			self.__addItem(object)
		elif isinstance(object, AuthRole):
			self.__addItem(object)
		elif issubclass(type(object), AuthRule):
			# print("add Rule")
			self.__addRule(object)

	def remove(self, object):
		if isinstance(object, AuthGroup):
			self.__removeGroup(object)
		elif isinstance(object, AuthPermission):
			self.__removeItem(object)
		elif isinstance(object, AuthRole):
			self.__removeItem(object)
		elif isinstance(object, AautRule):
			self.__removeRule(object)

	def update(self, name, object):
		# print("UPDATE ITEM Parent Called")
		if isinstance(object, AuthGroup):
			self.__updateGroup(name, object)
		elif isinstance(object, AuthPermission):
			self.__updateItem(name, object)
		elif isinstance(object, AuthRole):
			self.__updateItem(name, object)
		elif issubclass(type(object), AuthRule):
			self.__updateRule(name, object)

	def getRole(self, name):
		item = self.__getItem(name)
		if issubclass(type(item), Auth) and item.type == self.TYPE_ROLE:
			return item
		else:
			return None

	def getPermission(self, name):
		item = self.__getItem(name)
		if issubclass(type(item), Auth) and item.type == self.TYPE_PERMISSION:
			return item
		else:
			return None

	def getGroup(self, name):
		cur = self.db.getDb()
		q = """
			select * from {group} where name = %(name)s limit 1
		""".format(group=self.__table["groupTable"])
		qp = {"name": name}
		cur.execute(q, qp)
		if cur.rowcount != 1:
			return None
		row = cur.fetchone()
		group = AuthGroup(row["name"])
		group.description = row["description"]
		group.created = row["created_at"]
		group.updated = row["updated_at"]
		return group

	def rule(self, rulepath):
		try:
			module_name, class_name = rulepath.rsplit(".", 1)
			MyClass = getattr(importlib.import_module(rulepath), class_name)
			instance = MyClass()
			return instance
		except Exception:
			raise ValueError("Cant Init Rule {rule}".format(rule=rulepath))

	def getRule(self, name):
		# print(bool(self.rules))
		if bool(self.rules) == (not False):
			if name in self.rules:
				return self.rules[name]
			else:
				return None
		# print("GetFromDB")
		cur = self.db.getDb()
		q = """
			select data from {rule} where name = %(name)s limit 1
		""".format(rule=self.__table["ruleTable"])
		qp = {"name": name}
		cur.execute(q, qp)
		if cur.rowcount != 1:
			return None
		row = cur.fetchone()
		if row["data"] == None:
			return None
		return pickle.loads(row["data"])
		# with open(row["data"],'rb') as pickle_file:
		# 	data = pickle.load(row["data"])
		# 	return data

	def getAssignment(self,roleName,userId=None):
		if userId == None:
			return None
		cur = self.db.getDb()
		q=""" 
			select * from {assignment} where user_id=%(user_id)s and item_name=%(roleName)s limit 1
		""".format(assignment=self.__table["assignmentTable"])
		qp={"user_id":userId,"roleName":roleName}
		cur.execute(q,qp)
		if cur.rowcount != 1:
			return None
		row = cur.fetchone()
		asg = AuthAssignment(row)
		return asg
	
	def getRoles(self):
		return self.__getItems(self.TYPE_ROLE)

	def getDefaultRoleInstances(self):
		pass

	def getPermissions(self):
		return self.__getItems(self.TYPE_PERMISSION)

	def getPermissionsGrouped(self):
		cur = self.db.getDb()
		q=""" 
			select * from {group} where type = %(type)s
		""".format(group=self.__table["itemTable"])
		qp = {"type":self.TYPE_PERMISSION}
		cur.execute(q,qp)
		permissions = {}
		res = cur.fetchall()
		for row in res:
			if row["group"] == None:
				row["group"] = "Ungrouped"
			if row["group"] not in permissions:
				permissions[row["group"]] = {}
				permissions[row["group"]]["group"] = self.getGroup(row["group"])
				permissions[row["group"]]["member"] = []
			permission = self.populateItem(row)
			permissions[row["group"]]["member"].append(permission)
		return permissions

	def getGroups(self):
		cur = self.db.getDb()
		q=""" 
			select * from {group}
		""".format(group=self.__table["groupTable"])
		cur.execute(q)
		groups = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				grp = AuthGroup()
				grp.name = row["name"]
				grp.description = row["description"]
				grp.created = row["created_at"]
				grp.updated = row["updated_at"]
				groups[grp.name] = grp
		return groups

	def getRules(self):
		if bool(self.rules) == (not False):
			return self.rules
		cur = self.db.getDb()
		q="""
			select * from {rule}
		""".format(rule=self.__table["ruleTable"])
		cur.execute(q)
		rules = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			if row in res:
				data = row["data"]
				if data == None:
					rule = None
				else:
					rule = pickle.loads(data)
				if not issubclass(type(rule), AuthRule):
					rules[row["name"]] = rule
		return rules

	def getAssignments(self,userId = None):
		if userId == None:
			return {}
		cur = self.db.getDb()
		q="""
			select * from {assignment} where user_id = %(userId)s
		""".format(assignment=self.__table["assignmentTable"])
		qp={"userId":userId}
		# try:
		cur.execute(q,qp)
		# except Exception as e:
		# 	print(cur._last_executed)
		assignments = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				asg = AuthAssignment(row)
				assignments[row["item_name"]] = asg
		return assignments

	def executeRule(self, user, item, params):
		# if item.rule_name == None:
		# 	return True
		# print("check item",item,hasattr(item, 'rule_name'))
		if hasattr(item, 'rule_name') == False or item.rule_name == None:
			return True
		rule = self.getRule(item.rule_name)
		if issubclass(type(rule), AuthRule):
			return rule.execute(user, item, params)
		else:
			raise ValueError("Not Found Rule {rule}".format(rule=item.rule_name))

	def getRolesByUser(self,userId = None):
		cur = self.db.getDb()
		# userId = userId.strip()
		if userId == None:
			return {}
		q="""
		select b.* from {assignment} a, {item} b 
		where a.item_name = b.name
		and a.user_id=%(userId)s and b.type=%(type)s
		""".format(assignment=self.__table["assignmentTable"],item=self.__table["itemTable"])
		qp={"userId":userId,"type":self.TYPE_ROLE}
		cur.execute(q,qp)
		roles = {}
		if cur.rowcount > 0:
			res = cur.fetchall()
			for row in res:
				roles[row["name"]] = self.populateItem(row)		
		return roles

	def getChildRoles(self, roleName):
		role = self.getRole(roleName)
		if role == None:
			raise ValueError("Role {role} Not Found".format(role=roleName))
		result = {}
		self.__getChildrenRecursive(roleName,self.__getChildrenList(),result)
		roles = {roleName:role}
		tempRole = self.getRoles()
		for tr in tempRole:
			if tr.name in result:
				roles[tr.name] = tr
		return roles

	def getPermissionsByRole(self, roleName):
		if isinstance(roleName,AuthRole):
			roleName = roleName.name
		# roleName = role.name
		childrenList = self.__getChildrenList()
		result = {}
		self.__getChildrenRecursive(roleName, childrenList, result)		
		if bool(result) == False:
			return {}
		cur = self.db.getDb()
		q="""
			select * from {item} where type=%(type)s and name in %(names)s
		""".format(item=self.__table["itemTable"])
		qp={"type":self.TYPE_PERMISSION,"names":list(result.keys())}
		cur.execute(q,qp)
		permissions = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				permissions[row["name"]]=self.populateItem(row)
		return permissions
	
	def getPermissionsByUser(self, userId = None):
		if userId == None:
			return {}
		cur = self.db.getDb()
		q="""
			select * from {assignment} where user_id = %(userId)s
		""".format(assignment=self.__table["assignmentTable"])
		qp={"userId":userId}
		cur.execute(q,qp)
		assignments = {}
		if cur.rowcount > 0:
			res = cur.fetchall()
			for row in res:
				# print(row)
				asg = AuthAssignment(row)
				assignments[row["item_name"]] = asg
		return assignments
	
	def canAddChild(self,parent,child):
		return not self.__detectLoop(parent,child)

	def addChild(self, parent, child):
		cur = self.db.getDb()
		if parent.name == child.name:
			raise ValueError("Cannot add '{name}' as a child of itself.".format(name=parent.name))

		if isinstance(parent, AuthPermission) and isinstance(child, AuthRole):
			raise ValueError("Cannot add a role as a child of a permission")

		if self.__detectLoop(parent, child):
			raise ValueError("Cannot add '{childname}' as a child of '{parentname}'. A loop has been detected.".format(
				childname=child.name, parentname=parent.name))

		q = """ insert into {} values (%(parent)s,%(child)s) """.format(
			self.__table["itemChildTable"])
		qp = {"parent": parent.name, "child": child.name}
		cur.execute(q, qp)
		self.invalidateCache()
		return True

	def removeChild(self,parent,child):
		cur = self.db.getDb()
		q = """
			delete from {} where parent = %(parent)s and child = %(child)s
		""".format(self.__table["itemChildTable"])
		qp = {"parent": parent.name,"child":child.name}
		cur.execute(q, qp)
		self.invalidateCache()
		if cur.rowcount > 0:
			return True
		else:
			return False

	def removeChildren(self, parent):
		cur = self.db.getDb()
		q = """
			delete from {} where parent = %(parent)s
		""".format(self.__table["itemChildTable"])
		qp = {"parent": parent.name}
		cur.execute(q, qp)
		self.invalidateCache()
		if cur.rowcount > 0:
			return True
		else:
			return False

	def hasChild(self,parent,child):
		cur = self.db.getDb()
		q="""
			select * from {item} where parent = %(parent)s and child=%(child)s limit 1
		""".format(item = self.__table["itemChildTable"])
		qp={"parent":parent.name,"child":child.name}
		cur.execute(q,qp)
		if cur.rowcount > 0:
			return True
		else:
			return False

	def getChildren(self, name):
		cur = self.db.getDb()
		q = """
		select name, type, description, rule_name, data, created_at, updated_at
		from {auth_item},{auth_item_child}
		where (parent = %(parent)s) AND (`name`= child )
		""".format(auth_item=self.__table["itemTable"], auth_item_child=self.__table["itemChildTable"])
		qp = {
			"parent": name
		}
		child = {}
		cur.execute(q, qp)
		if cur.rowcount > 0:
			res = cur.fetcall()
			for row in res:
				if row["type"] == self.TYPE_ROLE:
					child[row["name"]] = self.populateItem(row)
		return child
	
	def __detectLoop(self, parent, child):
		if parent.name == child.name:
			return True
		for grandchild in self.getChildren(child.name):
			if self.__detectLoop(parent, child):
				return True
		return False

	def assign(self, role, userId):
		assigment = AuthAssignment()
		assigment.userId = userId
		assigment.roleName = role.name
		assigment.createdAt = int(time.time())

		cur = self.db.getDb()
		q = """
			insert into {table} values (%(item_name)s,%(user_id)s,%(cat)s)
		""".format(table=self.__table["assignmentTable"])
		qp = {
			"item_name": assigment.roleName,
			"user_id": assigment.userId,
			"cat": assigment.createdAt
		}
		cur.execute(q, qp)
		self.__checkAccessAssignments.pop(userId, None)
		return assigment
	
	def revoke(self, role=None, userId=None):
		if userId == None:
			return False
			# raise ValueError("USerid and RoleName Must Be Given, 0 Given")
		self.__checkAccessAssignments.pop(userId, None)
		q = """delete from {table} where user_id=%(userid)s and item_name=%(role)s""".format(
			table=self.__table["assignmentTable"])
		qp = {"userid": userId, "role": role.name}
		cur = self.db.getDb()
		cur.execute(q, qp)
		return cur.rowcount > 0

	def revokeAll(self, userId=None):
		if userId == None:
			return False
			# raise ValueError("USerid and RoleName Must Be Given, 0 Given")
		self.__checkAccessAssignments.pop(userId, None)
		q = """delete from {table} where user_id=%(userid)s """.format(
			table=self.__table["assignmentTable"])
		qp = {"userid": userId}
		cur = self.db.getDb()
		cur.execute(q, qp)
		return cur.rowcount > 0
	
	def removeAll(self):
		cur = self.db.getDb()
		self.removeAllAssignments()
		q1=""" delete from {itemChild} """.format(itemChild=self.__table["itemChildTable"])
		q2=""" delete from {item} """.format(item=self.__table["itemTable"])
		q3=""" delete from {rule} """.format(rule=self.__table["ruleTable"])
		cur.execute(q1)
		cur.execute(q2)
		cur.execute(q3)
		self.invalidateCache()

	def removeAllPermissions(self):
		self.__removeAllItems(self.TYPE_PERMISSION)
	
	def removeAllRoles(self):
		self.__removeAllItems(self.TYPE_PERMISSION)

	def __removeAllItems(self, utype):
		# no cascade check make it if you use database that do not support cascade
		# if (!$this->supportsCascadeUpdate()) {
		#     $names = (new Query())
		#         ->select(['name'])
		#         ->from($this->itemTable)
		#         ->where(['type' => $type])
		#         ->column($this->db);
		#     if (empty($names)) {
		#         return;
		#     }
		#     $key = $type == Item::TYPE_PERMISSION ? 'child' : 'parent';
		#     $this->db->createCommand()
		#         ->delete($this->itemChildTable, [$key => $names])
		#         ->execute();
		#     $this->db->createCommand()
		#         ->delete($this->assignmentTable, ['item_name' => $names])
		#         ->execute();
		# }
		cur = self.db.getDb()
		q="""
			delete from {item} where type = %(type)s
		""".format(item=self.__table["itemTable"])
		qp={"type":utype}
		cur.execute(q,qp)
		self.invalidateCache()
	
	def removeAllRules(self):
		cur = self.db.getDb()
		# if (!$this->supportsCascadeUpdate()) {
		#     $this->db->createCommand()
		#         ->update($this->itemTable, ['rule_name' => null])
		#         ->execute();
		# }
		q=""" delete from {rule} """.format(rule=self.__table["ruleTable"])
		cur.execute(q)
		self.invalidateCache()
	
	def removeAllAssignments(self):
		self.__checkAccessAssignments = {}
		q=""" delete from {assigment} """.format(assigment=self.__table["assignmentTable"])
		cur.execute(q)

	def getUserIdsByRole(self,roleName = None):
		if roleName == None:
			return {}
		q=""" 
			select user_id from {assigment} where item_name = %(item_name)s
		""".format(assigment=self.__table["assignmentTable"])
		qp={"item_name":roleName}
		cur = self.db.getDb()
		cur.execute(q,qp)
		users = []
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				users.append(row["user_id"])
		return users

	def loadFromCache(self):
		if self.items != None:
			return True

		data = self.c.get(self.cacheKey)
		if isinstance(data, dict) and 'items' in data and 'rules' in data and 'parents' in data:
			self.items = data['items']
			self.rules = data['rules']
			self.parents = data['parents']
			return True

		cur = self.db.getDb()
		q="""select * from {item}""".format(item=self.__table["itemTable"])
		cur.execute(q)
		self.items = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				self.items[row["name"]]=self.populateItem(row)

		q="""select * from {rule}""".format(rule=self.__table["ruleTable"])
		cur.execute(q)
		self.rules = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				if row["data"] == None:
					rule = None
				else:
					rule = pickle.loads(row["data"])				
				if not issubclass(type(rule), AuthRule):
					self.rules[row["name"]] = rule
		
		q="""select * from {itemChild}""".format(itemChild=self.__table["itemChildTable"])
		cur.execute(q)
		self.parents = {}
		if cur.rowcount > 0 :
			res = cur.fetchall()
			for row in res:
				if row["child"] in self.items :
					if row["child"] in self.parents:
						self.parents[row["child"]] = []
					self.parents[row["child"]].append(row["parent"])
		tmpCache = {
			"items":self.items,
			"rule":self.rules,
			"parents":self.parents
		}
		self.c.set(self.cacheKey,tmpCache)
		# self.c.set("auth_items",self.items)
		# self.c.set("auth_rules",self.rules)
		# self.c.set("auth_parents",self.parents)

	def hasNoAssignments(self, assignments={}):
		# if not bool(assignments) == True and bool(self.defaultRoles) == False:
		# 	return False
		# else:
		# 	return True

		if not bool(assignments) == True and not self.defaultRoles:
			return True
		else:
			return False

	def invalidateCache(self):
		if self.c.has(self.cacheKey):
			self.c.set(self.cacheKey, {})
			self.items = {}
			self.rules = {}
			self.parents = {}
			self.groups = {}
		self.__checkAccessAssignments = {}

	def populateItem(self, row):
		clas = AuthRole(
			row["name"]) if row["type"] == self.TYPE_ROLE else AuthPermission(row["name"])
		if row["data"] == None:
			data = None
		else:
			data = row["data"]

		clas.name = row["name"]
		clas.type = row["type"]
		clas.description = row["description"]
		clas.rule = row["rule_name"]
		clas.group = row["group"]
		clas.data = data
		clas.created = row["created_at"]
		clas.updated = row["updated_at"]
		return clas

	# @property
	# def type(self):
	# 	return self.__type

	# def getAssignments(self, userid=None):
	# 	if userid is None or userid.strip == "":
	# 		return {}

	# 	cur = self.db.getDb()
	# 	q = """select * from {table} where user_id=%(userid)s""".format(table=self.__table["authAssignmentTable"])
	# 	qp = {"userid": userid}
	# 	cur.execute(q, qp)
	# 	assignments = {}
	# 	if cur.rowcount > 0:
	# 		res = cur.fetcall()
	# 		for row in res:
	# 			assignments[row["item_name"]] = AuthAssignment({
	# 				"user_id": row["user_id"],
	# 				"item_name": row["item_name"],
	# 				"created_at": row["created_at"]
	# 			})
	# 	return assignments

	# def tessss(self):
		# try:
		# c = locate("project.helper.RBAC.TestClasss")
		# cl = getattr(c, "TestClass")
		# return c

		# 	found = True
		# except Exception:
		# 	found = False

		# return found
