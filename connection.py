# https://realpython.com/python-sql-libraries
# https://stackoverflow.com/a/71604821
import json

from mysql import connector

SCHEMA_VERSION = 1

with open("auth.json", "r") as authfile:
	auth = json.load(authfile)
	cxn = connector.connect(
		host=auth["host"],
		user=auth["user"],
		password=auth["password"],
		database=auth["database"]
	)

cursor = cxn.cursor()
cursor.execute("SELECT * FROM InstanceGlobals")
assert cursor.fetchall()[0][0] == SCHEMA_VERSION, "Incorrect schema version"
