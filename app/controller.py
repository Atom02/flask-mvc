from flask_classy import FlaskView
from project import app, socketio, cache
from flask import render_template,url_for,abort,make_response,g,session
from app.RequestRedirect import RequestRedirect
from app.User import User
from app.RBAC.AuthManager import AuthManager
from app.MyDb import MyDb
from datetime import timedelta
import pprint
import types
class controller(FlaskView):
    def __init__(self):
        fl = types.SimpleNamespace()        
        fl.app = app
        fl.cache = cache
        fl.socketio = socketio

        pagedata = types.SimpleNamespace()
        pagedata.title = app.config["NAME"]
        pagedata.description = app.config["NAME"]
        
        self.fl = fl
        self.pagedata = pagedata
        # pass
    acl = {
        "DB":app.config["DB"],
        "denyCallback":(lambda x,y: abort(403)),
        "rules":[]
    }
    defAcl = {
        "allow" : True,
        "action": "*",
        "matchCallback":None,
        "denyCallback":None,
        "roles": "*"
    }
    aclDB = None
    layout = None
    def aclCheck(self,name):
        bhv = self.behaviors()
        acl = {**self.acl,**bhv}
        if not acl["rules"]:
            return True
        self.aclDB = MyDb(acl["DB"])

        for p in acl["rules"]:
            perm = {**self.defAcl,**p}
            # print(perm)
            if perm["action"] == "*" or name in perm["action"]:
                match = self.aclRoleCheck(perm["roles"])  
                # print(name,match)              
                if match["status"]:
                    if perm["matchCallback"] is not None:
                        rule = match["with"]
                        return perm["matchCallback"](rule,name)

                    if not perm["allow"] and perm["denyCallback"] is not None:
                        rule = match["with"]
                        # print("denied")
                        t = perm["denyCallback"](rule,name)
                        if hasattr(t,"headers"):
                            head = dict(t.headers)
                            # print(head)
                            if t.status_code == 301 or t.status_code == 302:
                                raise RequestRedirect(t.location, code=t.status_code)
                        return perm["denyCallback"](rule,name)

                    elif not perm["allow"]:
                        # print("denied")
                        rule = match["with"]
                        return acl["denyCallback"](rule,name)
                    
                    elif perm["allow"]:
                        return perm["allow"]
                
                
            # if name in perm["action"]:
            #     allowed = perm["allow"]
            # else:
            #     allowed = not perm["allow"]

    def aclRoleCheck(self,roles):
        match = False
        user = User.current()
        isthere = [""]
        if roles == "*":            
            match = True
        elif roles == "?":            
            if user is None:
                isthere = ["UN AUTHRIZE USER"]
                match = True
        elif roles == "@":
            if user is not None:
                match = True
        else:
            if not roles:
                raise ValueError("Roles cannot be empty list, it must either *,@,?, or non empty list of role in stirng")
            if user is None:
                match = False
                isthere = ["UN AUTHRIZE USER"]
            else:
                auth = AuthManager(self.aclDB)
                userRoles = auth.getRolesByUser(user["id"])
                userRoles = list(userRoles.keys())
                # print("A",user,userRoles)
                isthere = [i for i in userRoles if i in roles]
                if not isthere:
                    match = False
                    isthere = [""]
                else:
                    match = True        
        return {"status":match,"with":isthere[0]}

    def __invokeDeny(self):
        pass
    def __getUser(self):
        pass

    def behaviors(self):
        return {}
    def before_request(self, name, *args, **kwargs):
        # session.permanent = True
        # app.permanent_session_lifetime = timedelta(days=31)
        if self.layout is not None:
            app.config["layout"]=self.layout        
        self.aclCheck(name)
        g.db = MyDb()
        pass

    def after_request(self, name, response):
        if g.db is not None:
            print('closing connection')
            g.db.close()
        return response

    def render(self,page,data={}):
        pagedata = {}
        pagedata["pagedata"] =self.pagedata
        z = {**pagedata,**data}
        resp = make_response(render_template(page,**z))
        return resp
        
