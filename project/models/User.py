from project import app
from app.MyDb import MyDb
from flask import g
import time
import string
import random
import bcrypt
from app.User import User
import datetime
import pytz
class User(User):
	statusList = {
		1:"Active",
		0:"Inactive",
		99:"Banned"
	}
	notAllowList = {
		0:"Inactive",
		99:"Banned"
	}
	def __init__(self):
		super().__init__()
		self.username = None
		self.name = None
		self.__id = None
		self.auth_key = None
		self.password_hash = None
		self.password_reset_token = None
		self.email = None
		self.created_at = None
		self.updated_at = None
		self.status = 1
		self.created_by = None
		self.__salt = None
		self.__user = None

		# self.STATUS_ACTIVE = 1
		# self.STATUS_DISABLED = 2
		# self.STATUS_DELETED = 0
		self.status=1

	def random_generator(self,size=32, chars = string.ascii_letters + string.digits + string.punctuation):
		# print(chars)
		return ''.join(random.choice(chars) for _ in range(size))
	
	def genSalt(self):
		return bcrypt.gensalt()

	def setPassword(self,password):
		salt = self.genSalt()
		passwd = password.encode()
		hashed = bcrypt.hashpw(passwd, salt)
		self.password_hash = hashed

	@staticmethod
	def validatePassword(pass1,password):
		salt = self.genSalt()
		passwd = password.encode()
		ecp = pass1.encode()
		if ecp == bcrypt.hashpw(passwd, ecp):
			return True
		else:
			return False

	def generateAuthKey(self):
		self.auth_key = self.random_generator()
		# print (self.auth_key)

	def save(self):		
		msg = ""
		self.generateAuthKey()
		# self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
		tz = pytz.timezone("UTC")
		today = datetime.datetime.now(tz)
		self.created_at = today.strftime("%Y-%m-%d %H:%M:%S")
		try:
			# print("TRY")
			status = True
			db = self._User__getDb()
			cur=db.getDb()
			q = """insert into users (user_name,name,auth_key,password_hash,created_at, status, created_by,email)
			values (%(user_name)s,%(name)s,%(auth_key)s,%(password_hash)s,%(created_at)s,%(status)s,%(created_by)s,%(email)s)"""
			cur.execute(q,{
				'user_name':self.username,
				'name':self.name,
				'auth_key':self.auth_key,
				'password_hash':self.password_hash,
				'created_at':self.created_at,
				'status':self.status,
				'created_by':self.created_by,
				'email':self.email
				})

			self.__id = cur.lastrowid
			self._User__commitDb()

		except MySQLError as e:
			status = False
			msg = 'Got error {!r}, errno is {}'.format(e, e.args[0])
		except pymysql.InternalError as e:
			status = False
			code, message = error.args
			msg = ">>>>>>>>>>>>>"+str(code)+str(message)
		except Exception as e:
			status = False
			msg = str(e)
		finally:
			# print(cur._last_executed)
			# self._User__closeDb()
			return {
				"status": status,
				"msg":msg,
				"id":self.__id
				}

	def update(self):		
		msg = ""
		# self.generateAuthKey()
		# self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
		tz = pytz.timezone("UTC")
		today = datetime.datetime.now(tz)
		try:
			print("TRY")
			status = True
			db = self.__getDb()
			cur=db.getDb()
			q = """
			update users set
			user_name=%(user_name)s,
			name=%(name)s,
			status=%(status)s,
			updated_at = %(updated_at)s,
			email=%(email)s 
			where user_id=%(id)s """
			qp = {
				'id':self.__id,
				'user_name':self.username,
				'name':self.name,
				'status':self.status,
				'email':self.email,
				"updated_at":today.strftime("%Y-%m-%d %H:%M:%S")
				}			
			cur.execute(q,qp)	
			if self.password_hash is not None:
				q=""" update users set
				password_hash=%(pwd)s
				where user_id=%(id)s """
				qp = {
					"pwd":self.password_hash,
					"id":self.__id
				}
				cur.execute(q,qp)

			self.__commitDb()

		except MySQLError as e:
			status = False
			msg = 'Got error {!r}, errno is {}'.format(e, e.args[0])
		except pymysql.InternalError as e:
			status = False
			code, message = error.args
			msg = ">>>>>>>>>>>>>"+str(code)+str(message)
		except Exception as e:
			status = False
			msg = str(e)
		finally:
			# print(cur._last_executed)
			self.__closeDb()
			return {
				"status": status,
				"msg":msg,
				"id":self.__id
				}


	@staticmethod
	def findByUsername(username,returnClass = False):
		try:
			db = MyDb()
			cur = db.getDb()
			q="""select * from users where user_name=%(username)s limit 1"""
			cur.execute(q,{"username":username})
			if(cur.rowcount>0 ):
				res = cur.fetchone()
				if returnClass is True:
					res2 = User()
					res2.__id = res["user_id"]
					res2.username = res["user_name"]
					res2.name = res["name"]
					res2.password_hash = res["password_hash"]
					res2.email = res["email"]
					res2.created_at = res["created_at"]
					res2.updated_at = res["updated_at"]
					res2.status = res["status"]
					res2.created_by = res["created_by"]
					res = res2
				return res
			else:
				raise Exception("User Not Found")
		except Exception as e:
			print(e)
			return None
		finally:
			db.close()
	@staticmethod	
	def findById(id,returnClass = False):
		try:
			db = MyDb()
			cur = db.getDb()
			q=""" select * from users where user_id=%(userid)s limit 1 """
			cur.execute(q,{"userid":id})
			# print(cur._last_executed,cur.rowcount != 1)
			if cur.rowcount != 1:
				raise Exception("User Not Found")
			else:
				res = cur.fetchone()
				if returnClass is True:
					res2 = User()
					res2.__id = res["user_id"]
					res2.username = res["user_name"]
					res2.name = res["name"]
					res2.password_hash = res["password_hash"]
					res2.email = res["email"]
					res2.created_at = res["created_at"]
					res2.updated_at = res["updated_at"]
					res2.status = res["status"]
					res2.created_by = res["created_by"]
					print ("found",res2.__id,res["user_id"])
					res = res2					
				return res
		except Exception as e:
			print(e)
			return None

	
	@staticmethod	
	def getStatus(key):
		return User.statusList[key]

	def getId(self):
		print("GET ID",self.__id)
		return self.__id
	