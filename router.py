# flask --app router run

from functools import wraps

from flask import Flask, make_response, render_template, request, redirect

from model import M

app = Flask(__name__)

def ensure_args(keys): # recieve keys
	def decorator(func): # recieve function
		@wraps(func)
		def wrapper(*args, **kwargs): # wrapper function that runs
			missing = set(keys) - set(request.form)
			if not missing: return func(*args, **kwargs)
			return f"Required request arguments {', '.join(missing)} missing", 400
		return wrapper
	return decorator

@app.route('/')
def home():
	id, logged_in = M.user_of_token(request.cookies.get("token"))
	return render_template("beta.html", logged_in = logged_in, user_id = id)

@app.route("/user/login", methods=["POST"])
@ensure_args(["username","password"])
def user_login():
	value, code = M.user_login(request.form["username"], request.form["password"])
	if code != 200:
		return value, code
	else:
		resp = make_response(redirect("/"))
		resp.set_cookie("token", value, secure=True, httponly=True, max_age=60*60, samesite="strict")
		return resp

@app.route("/user/changeColor", methods=["POST"])
@ensure_args(["color"])
def user_changeColor():
	token = request.cookies.get("token")
	value, worked = M.user_of_token(token)
	return M.user_changeColor(request.form["color"], value) if worked else (value, 401)

@app.route("/user/logOut", methods=["POST"])
def user_logOut():
	token = request.cookies.get("token")
	value, worked = M.user_of_token(token)
	if not worked:
		return value, 401
	else:
		resp = make_response(M.user_logOut(token))
		resp.delete_cookie("token")
		return resp

@app.route("/users/new", methods=["POST"])
@ensure_args(["username","email"])
def users_new():
	return M.users_new(request.form["username"], request.form["email"])
