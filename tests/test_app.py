"""The app factory and the schema version check."""
import pytest

from app import create_app


def test_app_starts_with_the_right_schema_version(app):
	assert app.testing


def test_wrong_schema_version_stops_the_app(app, query):
	query("UPDATE InstanceGlobals SET SchemaVersion = 99")
	with pytest.raises(RuntimeError, match="schema version 99"):
		create_app({"TESTING": True, "DATABASE": app.config["DATABASE"]})
