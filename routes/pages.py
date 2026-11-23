"""Page routes. For now only the home page, moved from router.py without changing behavior."""
from flask import Blueprint, render_template, request

from models import users

bp = Blueprint("pages", __name__)

@bp.route('/')
def home():
	id, logged_in = users.user_of_token(request.cookies.get("token"))
	return render_template("beta.html", logged_in = logged_in, user_id = id)
