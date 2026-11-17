# https://realpython.com/python-sql-libraries
import json
import secrets
import string
from hashlib import sha256

from mysql import connector
from mysql.connector.errors import *

SCHEMA_VERSION = 1

class Model:
	cxn = None
	db = None

	def __init__(self):
		with open("auth.json", "r") as authfile:
			auth = json.load(authfile)
			self.cxn = connector.connect(
				host=auth["host"],
				user=auth["user"],
				password=auth["password"],
				database=auth["database"]
			)

		cursor = self.cxn.cursor()
		cursor.execute("SELECT * FROM InstanceGlobals")
		assert cursor.fetchall()[0][0] == SCHEMA_VERSION, "Incorrect schema version"

	def users_new(self, username, email):
		alphabet = string.ascii_letters + string.digits
		password = ''.join(secrets.choice(alphabet) for i in range(20))
		hashed_password = sha256(password.encode()).hexdigest()

		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()
		try:
			cursor.execute("INSERT INTO Users (Name, Email, HashedPass, Color) VALUES (%s, %s, %s, %s)", (username, email, hashed_password, "#fff"))
			self.cxn.commit()
			return password, 200

		except IntegrityError:
			return "Username already in use", 400

M = Model()
