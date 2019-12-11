import os
import random
import string
from project import app
from flask import session
from app.RBAC.AuthManager import AuthManager
from app.MyDb import MyDb
from app.model import model
class User(model):
    def __init__(self):
        super().__init__()

    def __init__(self):
        self.db = None
        self._model__dbLocale = False
    
    def __getDb(self):
        if self.db is None:
            self.db = g.db
            self._model__dbLocale = True
        return self.db
    
    def __closeDb(self):		
        if self._model__dbLocale is False:			
            return True		
        else:
            self.db.close()
    def __commitDb(self):
        if self._model__dbLocale is False:
            return True
        else:
            self.db.commit()

    @staticmethod
    def can(itemName,params={}):
        # print("USER SET")
        check = User.checkLogin()
        if not check:
            return False
        db = MyDb()
        user = User.get()
        auth = AuthManager(db)
        # print("CAN ",user["id"],permissionName)
        return auth.checkAccess(user["id"],itemName,params)
             
    @staticmethod
    def set(user):
        # key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        # if "usersessionid" not in app.config:
        #     app.config['usersessionid'] = key
        # sid = app.config['usersessionid']
        session["user"] = user
        
    @staticmethod
    def get():
        # if "usersessionid" not in app.config:
        #     return False        
        # sid = app.config['usersessionid']
        sid = "user"
        if sid not in session:
            return False

        return session[sid]

    @staticmethod
    def current():
        # if "usersessionid" not in app.config:
        #     return None
        # sid = app.config['usersessionid']
        sid = "user"
        if sid not in session:
            return None
        return session[sid]

    @staticmethod
    def checkLogin():
        # if "usersessionid" not in app.config:
        #     return False
        
        # sid = app.config['usersessionid']
        sid = "user"
        if sid not in session:
            return False
        
        return True

    @staticmethod
    def destroy():
        # sid = app.config['usersessionid']
        sid = "user"
        session.pop(sid)
        pass