from flask import escape, session,render_template, request, Response, jsonify, make_response, abort, redirect, url_for, json, g
from app.controller import controller
from app.MyDb import MyDb
# from project.models.User import User
class FrontView(controller):
	layout = "layout/main.html"
	title = ""
	
	def before_request(self, name, *args, **kwargs):
		super().before_request(name)
		
	def after_request(self, name, response):
		return super().after_request(name, response)
	
	def cekPermission(self,permissions):
		super().cekPermission(permissions)