# -*- coding: utf-8 -*-
__version__ = '1.0.1'
from flask import Flask,redirect,url_for
from flask_socketio import SocketIO
import project.appConfig as cfgP
import project.appConfigLocal as cfgLocal
from flask_mobility import Mobility
from flask_session import Session
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
import types
import os
from datetime import timedelta
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

cfgTmp = [a for a in dir(cfgP) if not a.startswith('__')]
cfg = types.SimpleNamespace()
for c in cfgTmp:
	setattr(cfg,c,getattr(cfgP,c))
	if hasattr(cfgLocal, c):
		setattr(cfg,c,getattr(cfgLocal,c))


app = Flask('project')
csrf = CSRFProtect(app)
Mobility(app)

app.secret_key = 'changeToYourSecretKey' #'onehotonekill'

app.config["NAME"]="ProjectName"
app.config['SECRET_KEY'] = app.secret_key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 #32 Mega
app.config['CACHE_KEY_PREFIX']='pttimah'
app.config["CACHE_TYPE"]="simple"
app.config["CACHE_DEFAULT_TIMEOUT"]=600
app.config["CACHE_THRESHOLD"]=1000
app.config["SESSION_TYPE"]="filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
app.config['SESSION_PERMANENT'] = True 

app.config['COMPONENTS'] = cfg.components
app.config['DB'] = cfg.DB
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["ALLOWED_EXTENSIONS"] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# testing alchecmy but we will not use it
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+cfg.DB['user']+':'+cfg.DB['password']+'@'+cfg.DB['host']+':'+str(cfg.DB['port'])+'/'+cfg.DB['db']
# app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.url_map.strict_slashes = False
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.debug = True
app.jinja_env.add_extension("project.helper.JinjaExt.RelativeInclude")
app.jinja_env.add_extension("jinja2.ext.do")

socketio = SocketIO(app, cors_allowed_origins = ["*"])
cache = Cache(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# REGISTER YOUR ROUTE
from project.controllers import *
SiteController.SiteView.register(app)
