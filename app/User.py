import os
import random
import string
from project import app
from flask import session,g
from app.RBAC.AuthManager import AuthManager
import types
class User():
    # @staticmethod
    # def can(permissionName,params={}):
    #     check = User.checkLogin()
    #     if not check:
    #         return False
    #     sid = app.config['usersessionid']
    #     user = session[sid]
    #     rbac = AuthManager()
    #     return rbac.checkAccess()
    @staticmethod
    def can(itemName,params={}):
        # print("USER SET")
        check = User.checkLogin()
        if not check:
            return False
        db = g.db
        user = User.get()
        auth = AuthManager(db)
        # print("CAN ",user["id"],permissionName)
        print("USER CAN",itemName,auth.checkAccess(user.id,itemName,params))
        return auth.checkAccess(user.id,itemName,params)
    
    @staticmethod
    def get():
        # if "usersessionid" not in app.config:
        #     return False        
        # sid = app.config['usersessionid']
        sid = "user"
        # if session.get('user') != True:
        #     return False
        if sid not in session:
            return None
        f = types.SimpleNamespace()
        f.id = session[sid]['id']
        f.username = session[sid]['username']
        return f
        # return session[sid]

    @staticmethod
    def set(user):
        session["user"] = user
        # key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        # if "usersessionid" not in app.config:
        #     app.config['usersessionid'] = key
        # sid = app.config['usersessionid']
        # # print(sid)
        # session[sid] = user
    
    @staticmethod
    def current():
        # if "usersessionid" not in app.config:
        #     return None
        # sid = app.config['usersessionid']
        # if sid not in session:
        #     return None
        sid = "user"
        if sid not in session:
            return None
        return session["user"]

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