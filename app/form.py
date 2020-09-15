from wtforms import Form, Field, IntegerField, HiddenField, FormField, BooleanField, StringField, TextAreaField, FieldList, PasswordField, SelectMultipleField, validators, ValidationError
from app.RBAC.AuthManager import AuthManager
from app.MyDb import MyDb
class form(Form):
    # db = None
    def __init__(self, db = None):
        super().__init__()
        # if(db is None):
        #     raise ValueError("db required form(db)")
        self.db = db

    def addError(self,ername,msg=None):
        if ername not in self.errors:
            self.errors[ername]=[]
        if msg is None:
            msg = ername+" is error"
        self.errors[ername].append(msg)
    
    def addValidator(self,field,validator = None):
        if validator is None:
            return False
        if hasattr(self,field):
            f = getattr(self, field)
        else:
            return False
        isList = isinstance(validator,list)
        if f.validators == None:
            if isList:
                f.validator = validator
            else:
                f.validators = [validator]
        else:
            if isList:
                f.validator.extend(validator)
            else:
                f.validators.append(validator)