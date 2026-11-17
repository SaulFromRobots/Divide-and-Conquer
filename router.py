# flask --app router run
# curl -X POST http://127.0.0.1:5000/users/new -d "username=saul&email=saul.statman@sjsu.edu"

from functools import wraps

from flask import Flask, request

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

@app.route("/user/login", methods=["POST"])
@ensure_args(["username","password"])
def user_login():
	return M.user_login(request.form["username"], request.form["password"])

@app.route("/user/changeColor", methods=["POST"])
@ensure_args(["color","token"])
def user_changeColor():
	value, worked = M.user_of_token(request.form["token"])
	return M.user_changeColor(request.form["color"], value) if worked else (value, 401)

@app.route("/user/logOut", methods=["POST"])
@ensure_args(["token"])
def user_logOut():
	token = request.form["token"]
	value, worked = M.user_of_token(token)
	return M.user_logOut(token) if worked else (value, 401)

@app.route("/users/new", methods=["POST"])
@ensure_args(["username","email"])
def users_new():
	return M.users_new(request.form["username"], request.form["email"])
