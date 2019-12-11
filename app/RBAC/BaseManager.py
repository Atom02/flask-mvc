
from app.RBAC.AuthGroup import AuthGroup
from app.RBAC.AuthPermission import AuthPermission
from app.RBAC.AuthRole import AuthRole
from app.RBAC.AuthAssignment import AuthAssignment


class BaseManager():

    defaultRoles = {}

    def __init__(self):
        pass

    def getItem(self, name):
        pass

    def getItems(self, type):
        pass

    def addItem(self, item):
        pass

    def addRule(self, item):
        pass

    def removeItem(self, item):
        pass

    def removeRule(self, rule):
        pass

    def updateItem(self, item):
        pass

    def updateRule(self, rule):
        pass

    def createRole(self, name):
        role = AuthRole()
        role.name = name
        return role

    def createPermission(self, name):
        permission = AuthRole()
        permission.name = name
        return permission
