from project import app
from app.MyDb import MyDb
from flask import g
class model():
	def __init__(self):
		self.db = None
		self.cur = None
		# self.__dbLocale = False
	def getDb(self):
		if self.db is None:
			self.db = g.db
		# if self.cur is None:
		# 	self.cur = self.db.getDb() 
		return self.db
	# def __getDb(self):
	# 	if self.db is None:
	# 		self.db = g.db
	# 		self.__dbLocale = True
	# 	return self.db

	# def __closeDb(self):
	# 	if self.__dbLocale is False:
	# 		return True
	# 	else:
	# 		self.db.close()
	
	# def __commitDb(self):
	# 	if self.__dbLocale is False:
	# 		return True
	# 	else:
	# 		self.db.commit()