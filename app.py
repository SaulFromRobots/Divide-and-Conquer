"""Application factory (CS174-18, slides 37-39).

Run the development server from this folder with:
	flask --app app run --port 5001
"""
import json
import os

from flask import Flask

import db
from routes import pages, users


def create_app(test_config=None):
	"""Create and configure the app. Tests pass their own settings."""
	app = Flask(__name__)

	if test_config is None:
		# Database settings come from auth.json, which Git ignores
		# (CS174-18, slide 34). Copy auth.example.json to make your own.
		with open(os.path.join(app.root_path, "auth.json"), "r") as authfile:
			app.config["DATABASE"] = json.load(authfile)
	else:
		app.config.update(test_config)

	db.init_app(app)
	app.register_blueprint(pages.bp)
	app.register_blueprint(users.bp)

	# Stop now if the database doesn't match this code.
	with app.app_context():
		db.check_schema_version()

	return app
