"""Database connections: one connection per request.

Each request opens its own MySQL connection the first time it needs one,
keeps it on Flask's g, and closes it when the request ends.
Before, every request shared one connection, and the
server crashed when two requests used it at the same time.
"""
import mysql.connector
from flask import current_app, g

# The schema version this code expects. Raise it together with schema.sql.
SCHEMA_VERSION = 2


def get_db():
	"""Return this request's connection, opening it on first use."""
	if "db" not in g:
		g.db = mysql.connector.connect(**current_app.config["DATABASE"])
	return g.db


def close_db(error=None):
	"""Close this request's connection, if the request opened one."""
	db = g.pop("db", None)
	if db is not None:
		db.close()


def check_schema_version():
	"""Stop with a clear message if the database and the code disagree."""
	cursor = get_db().cursor()
	cursor.execute("SELECT SchemaVersion FROM InstanceGlobals")
	rows = cursor.fetchall()
	found = rows[0][0] if rows else None
	# An if, not an assert: Python removes asserts when it runs with -O.
	if found != SCHEMA_VERSION:
		raise RuntimeError(
			f"The database has schema version {found}, but this code needs "
			f"version {SCHEMA_VERSION}. Rebuild the database from schema.sql."
		)


def init_app(app):
	"""Close each request's connection when the request ends."""
	app.teardown_appcontext(close_db)
