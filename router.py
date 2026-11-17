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

@app.route("/users/new", methods=["POST"])
@ensure_args(["username","email"])
def users_new():
	return M.users_new(request.form["username"], request.form["email"])
