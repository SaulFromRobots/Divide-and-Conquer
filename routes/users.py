"""The /user/... and /users/... routes, moved from router.py without changing behavior."""

from __init__ import ensure_args
from flask import Blueprint, make_response, redirect, request

from models import users

bp = Blueprint("users", __name__)

@bp.route("/user/login", methods=["POST"])
@ensure_args(["username","password"])
def user_login():
	value, code = users.user_login(request.form["username"], request.form["password"])
	if code != 200:
		return value, code
	else:
		resp = make_response(redirect("/"))
		resp.set_cookie("token", value, secure=True, httponly=True, max_age=60*60, samesite="strict")
		return resp

@bp.route("/user/changeColor", methods=["POST"])
@ensure_args(["color"])
def user_changeColor():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)
	return users.user_changeColor(request.form["color"], value) if worked else (value, 401)

@bp.route("/user/logOut", methods=["POST"])
def user_logOut():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)
	if not worked:
		return value, 401
	else:
		resp = make_response(users.user_logOut(token))
		resp.delete_cookie("token")
		return resp

@bp.route("/users/new", methods=["POST"])
@ensure_args(["username","email"])
def users_new():
	return users.users_new(request.form["username"], request.form["email"])
