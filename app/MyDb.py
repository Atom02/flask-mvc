import pymysql
import pymysql.cursors
from pymysql.constants import FIELD_TYPE
from pymysql.converters import conversions as conv
from project import app
class MyDb:
	def __init__(self,params=None,removeConv=False):
		self.open = False
		self.db = None
		self.removeConv = removeConv
		# print(config['DB'])
		if params is not None:
			self.params=params
		else:
			self.params=app.config['DB']

		if self.params is not None:
			if removeConv:
				cf = conv.copy()
				del cf[FIELD_TYPE.DATE]
				del cf[FIELD_TYPE.DATETIME]
				del cf[FIELD_TYPE.TIME]
				self.db = pymysql.connect(host=self.params['host'],port=self.params['port'],
						user=self.params['user'],
						password=self.params['password'],
						db=self.params['db'],
						cursorclass=pymysql.cursors.DictCursor,conv=cf)
			else:	
				self.db = pymysql.connect(host=self.params['host'],port=self.params['port'],
							user=self.params['user'],
							password=self.params['password'],
							db=self.params['db'],
							cursorclass=pymysql.cursors.DictCursor)
			self.open = True
			self.cur=self.db.cursor()

	def reinit(self,removeConv=False):
		print('REINIT DB')
		self.__init__(self.params, removeConv)

	def openDb(self):
		if self.removeConv:
			cf = conv.copy()
			del cf[FIELD_TYPE.DATE]
			del cf[FIELD_TYPE.DATETIME]
			del cf[FIELD_TYPE.TIME]
			self.db = pymysql.connect(host=self.params['host'],port=self.params['port'],
						user=self.params['user'],
						password=self.params['password'],
						db=self.params['db'],
						cursorclass=pymysql.cursors.DictCursor,conv=cf)
		else:
			self.db = pymysql.connect(host=self.params['host'],port=self.params['port'],
						user=self.params['user'],
						password=self.params['password'],
						db=self.params['db'],
						cursorclass=pymysql.cursors.DictCursor)
		self.open = True
	def getDb(self):
		if(self.open is False):
			print("open db")
			self.openDb()
			self.cur=self.db.cursor()
		return self.cur
	def getCursor(self):
		return self.getDb()
	def close(self):
		self.db.cursor().close()
		self.db.close()
		self.cur = None
		self.open = False

	def getCon(self):
		return self.db

	def commit(self):
		self.db.commit()
	def rollback(self):
		self.db.rollback()

		