import os
import random
import string
from project import app
from flask import session
from app.RBAC.AuthManager import AuthManager
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
    def set(user):
        key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        if "usersessionid" not in app.config:
            app.config['usersessionid'] = key
        sid = app.config['usersessionid']
        print(sid)
        session[sid] = user
    
    @staticmethod
    def current():
        if "usersessionid" not in app.config:
            return None
        sid = app.config['usersessionid']
        if sid not in session:
            return None
        return session[sid]

    @staticmethod
    def checkLogin():
        if "usersessionid" not in app.config:
            return False
        
        sid = app.config['usersessionid']
        if sid not in session:
            return False
        
        return True

    @staticmethod
    def destroy():
        sid = app.config['usersessionid']
        session.pop(sid)
        pass