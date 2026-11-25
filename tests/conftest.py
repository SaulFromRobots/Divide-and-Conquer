"""Test setup: every test starts with fresh, empty tables in dac_test.

Tests never touch dac_dev or the shared database: they use a separate
test database (CS174-18, slide 55) on your own computer.
"""
import json
import pathlib

import mysql.connector
import pytest

from app import create_app

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST_DATABASE = "dac_test"


def settings_for_tests():
	"""Your auth.json settings, but pointed at dac_test."""
	with open(ROOT / "auth.json") as authfile:
		settings = json.load(authfile)
	if settings.get("host") not in ("localhost", "127.0.0.1"):
		raise RuntimeError("Tests only run on a MySQL server on this computer. Check auth.json.")
	settings["database"] = TEST_DATABASE
	return settings


def schema_statements():
	"""The statements in schema.sql, without the -- comment lines."""
	lines = [line for line in (ROOT / "schema.sql").read_text().splitlines()
		if not line.strip().startswith("--")]
	return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def rebuild_test_database(settings):
	"""Drop dac_test, create it again, and run schema.sql in it."""
	server = {key: value for key, value in settings.items() if key != "database"}
	cxn = mysql.connector.connect(**server)
	cursor = cxn.cursor()
	# TEST_DATABASE is a fixed name in this file, never user input.
	cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
	cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
	cursor.execute(f"USE `{TEST_DATABASE}`")
	for statement in schema_statements():
		cursor.execute(statement)
	cxn.commit()
	cxn.close()


@pytest.fixture
def app():
	settings = settings_for_tests()
	rebuild_test_database(settings)
	return create_app({"TESTING": True, "DATABASE": settings})


@pytest.fixture
def client(app):
	return app.test_client()


@pytest.fixture
def query(app):
	"""Run SQL directly on dac_test, to set up or check data."""
	def run(sql, params=()):
		cxn = mysql.connector.connect(**app.config["DATABASE"])
		try:
			cursor = cxn.cursor()
			cursor.execute(sql, params)
			rows = cursor.fetchall() if cursor.with_rows else None
			cxn.commit()
			return rows
		finally:
			# Close even when the SQL fails. An open connection keeps its
			# locks, and the next test then waits forever to drop dac_test.
			cxn.close()
	return run
