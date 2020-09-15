from flask_classy import FlaskView
from project import app
from flask import render_template,url_for,abort,g,make_response

from app.RequestRedirect import RequestRedirect
from app.User import User
from app.RBAC.AuthManager import AuthManager
from app.MyDb import MyDb
import pprint
class controller(FlaskView):
    connectDb = True
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
    pagedata = {}
    def aclCheck(self,name):
        bhv = self.behaviors()
        # print('bhv',str(bhv),str(self.acl))
        acl = {**self.acl,**bhv}
        if not acl["rules"]:
            return True
        self.aclDB = MyDb(acl["DB"])

        for p in acl["rules"]:
            perm = {**self.defAcl,**p}
            if perm["action"] == "*" or name in perm["action"]:
                match = self.aclRoleCheck(perm["roles"])
                # print('checking',perm,name,match)
                # if match["status"]:
                #     if perm["matchCallback"] is not None:
                #         rule = match["with"]
                #         # print("MATCHCALL")
                #         return perm["matchCallback"](rule,name)
                #     if not perm["allow"] and perm["denyCallback"] is not None:
                #         rule = match["with"]
                #         # print("denied")
                #         t = perm["denyCallback"](rule,name)
                #         if hasattr(t,"headers"):
                #             head = dict(t.headers)
                #             if t.status_code == 301 or t.status_code == 302:
                #                 raise RequestRedirect(t.location, code=t.status_code)
                #         return perm["denyCallback"](rule,name)
                #     elif not perm["allow"]:
                #         rule = match["with"]
                #         return acl["denyCallback"](rule,name)
                #     else:
                #         # print(name,"ALLOWED")
                #         return True
                if match["status"]:
                    # print("denied 0")
                    if perm["matchCallback"] is not None:
                        print("Match ExEcUTE")
                        rule = match["with"]
                        return perm["matchCallback"](rule,name)

                    if not perm["allow"] and perm["denyCallback"] is not None:
                        rule = match["with"]
                        # print("denied 1")
                        t = perm["denyCallback"](rule,name)
                        if hasattr(t,"headers"):
                            head = dict(t.headers)
                            # print(head)
                            if t.status_code == 301 or t.status_code == 302:
                                raise RequestRedirect(t.location, code=t.status_code)
                        return perm["denyCallback"](rule,name)

                    elif not perm["allow"]:
                        print("denied")
                        rule = match["with"]
                        return acl["denyCallback"](rule,name)
                    
                    elif perm["allow"]:
                        print("allowed")
                        return perm["allow"]
                
                
            # if name in perm["action"]:
            #     allowed = perm["allow"]
            # else:
            #     allowed = not perm["allow"]

    def aclRoleCheck(self,roles):
        match = False
        user = User.current()
        # print('user',user)
        isthere = [""]
        if roles == "*":
            # print('Match *')            
            match = True
        elif roles == "?":     
            # print('Match ?')        
            if user is None:
                # print('Match ? None') 
                isthere = ["UN AUTHRIZE USER"]
                match = True
        elif roles == "@":
            # print('Match @') 
            if user is not None:
                # print('Match * Not None') 
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
                isthere = [i for i in userRoles if i in roles]
                if not isthere:
                    match = False
                else:
                    match = True
        print(match,user,isthere)
        print(roles)
        return {"status":match,"with":isthere[0]}

    def __invokeDeny(self):
        pass
    def __getUser(self):
        pass

    def behaviors(self):
        return {}

    def before_request(self, name, *args, **kwargs):
        if self.connectDb is True:
            if not hasattr(g,"db"):
                g.db = MyDb()
        if self.layout is not None:
            app.config["layout"]=self.layout
        self.aclCheck(name)

    def after_request(self, name, response):
        # if hasattr(g,"db") and g.db.db is not None:
        #     g.db.close()
        return response
    
    def cekPermission(self,permissions):
        for p in permissions:
            if not User.can(p):
                abort(403)

    def render(self,page,data={}):
        pagedata = {}
        pagedata["pagedata"] =self.pagedata
        z = {**pagedata,**data}
        resp = make_response(render_template(page,**z))
        return resp