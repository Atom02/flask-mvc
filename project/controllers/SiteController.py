from flask import escape, session,render_template, request, Response, jsonify, make_response, abort, redirect, url_for, json, g
from flask_classy import route
from flask_restful import Api, Resource
from .FrontController import FrontView
from project import app
# from project.models.User import User
from app.RBAC.AuthManager import AuthManager


class SiteView(FrontView):
	connectDb = False
	def behaviors(self):
		acl = {
			"rules":[
				{
					"allow":True,
					"action":["logout"],
					"roles":"@"
				},
				{
					"allow":True,
					"action":["login","index"],
					"roles":"?"
				},
				{
					"allow":False,
					'action':"*",
					"roles":"?",
					"denyCallback":(lambda rule,action: abort(401))
				}
			]
		}
		return acl
	
	
	def before_request(self, name,*args, **kwargs):
		# print("ALWAYS RUN BEFORE ACTION")
		super().before_request(name)
		pass

	def index(self):
		return "ALIVE"
	# access using site/login
	@route("/login",methods=["POST","GET"])
	def login(self):
		# YOU CAN RENDER PAGE IN TEMPLATE FOLDER WITH
		data = {
			"some":"data"
		}
		return self.render("site/login.html",data)

	@route("/logout",methods=["GET"])
	def logout(self):
		session.clear()
		return jsonify({"status":"ok"})

		