# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask,redirect,url_for
from flask_socketio import SocketIO
import project.appConfig as cfg
import project.appComponents as cmps
from flask_mobility import Mobility
from werkzeug.contrib.cache import MemcachedCache
from flask_wtf.csrf import CSRFProtect


app = Flask('project')
csrf = CSRFProtect(app)
Mobility(app)

app.secret_key = 'xUYLx8o#))[1@K1pQvVrvHHKf7/' #'onehotonekill'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://candra:db_lapan2089@192.168.3.19:3306/santanu_live'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
app.config['SECRET_KEY'] = app.secret_key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['COMPONENTS'] = cmps
app.config['DB'] = cfg.DB
app.config['CACHE_KEY']='santanu_rbac'
app.config['BACKENDROUTE']='/office'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["ALLOWED_EXTENSIONS"] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# app.url_map.strict_slashes = False
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.debug = True
app.jinja_env.add_extension("project.helper.JinjaExt.RelativeInclude")
app.jinja_env.add_extension("jinja2.ext.do")
socketio = SocketIO(app, cors_allowed_origins = ["*"])


c = MemcachedCache(['localhost:11211'])
c.delete(app.config['CACHE_KEY'])
#jinja extention





# toolbar = DebugToolbarExtension(app)
from project.controllers import *
# TestClass.TestView.register(app)


from project.controllersBackend import *
# DashboardController.DashboardView.register(app,route_base=app.config['BACKENDROUTE']+'/dashboard')
# UsersController.UsersView.register(app,route_base=app.config['BACKENDROUTE']+'/users')
# RolesController.RolesView.register(app,route_base=app.config['BACKENDROUTE']+'/roles')