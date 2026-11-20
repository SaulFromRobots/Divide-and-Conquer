# https://realpython.com/python-sql-libraries
import json
import secrets
import string
from random import randrange

from mysql import connector
from mysql.connector.errors import *

import util

SCHEMA_VERSION = 1
SESSION_EXPIRE_MINUTES = 30

class Model:
	cxn = None

	def __init__(self):
		# Create a connection using DB info in the auth.json file
		with open("auth.json", "r") as authfile:
			auth = json.load(authfile)
			self.cxn = connector.connect(
				host=auth["host"],
				user=auth["user"],
				password=auth["password"],
				database=auth["database"]
			)

		# Make sure that the database is using the correct schema version
		cursor = self.cxn.cursor()
		cursor.execute("SELECT * FROM InstanceGlobals")
		if (cursor.fetchall()[0][0] != SCHEMA_VERSION):
			raise ValueError("Incorrect schema version")

	# If the token passed to the function is non-stale and exists, return the user ID associated with it. Otherwise return an error message.
	def user_of_token(self, token):
		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()

		# Clear stale sessions
		cursor.execute("DELETE FROM Sessions WHERE LastUsed < NOW() - INTERVAL %s MINUTE", (SESSION_EXPIRE_MINUTES,))

		# Find the user ID
		cursor.execute("SELECT UserID FROM Sessions WHERE Token = %s", (token,))
		user = cursor.fetchone()
		if user is None:
			resp = ("Invalid or expired user token", False)
		else:
			resp = (user[0], True)
			# If the session exists, extend the timeout
			cursor.execute("UPDATE Sessions SET LastUsed = NOW() WHERE token = %s", (token,))
		self.cxn.commit()
		return resp

	# All further functions perform actions corresponding to API endpoints

	def user_login(self, username, password):
		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()

		cursor.execute("SELECT HashedPass, ID FROM Users WHERE Name = %s", (username,))
		try:
			[hashed_pass,user_id] = cursor.fetchall()[0]
			if (hashed_pass != util.hash(password)):
				raise ValueError
		except:
			return "Bad username/password combination", 401

		token = secrets.token_urlsafe(192)

		cursor.execute("INSERT INTO Sessions (UserID, Token, LastUsed) VALUES (%s, %s, NOW())", (user_id, token))
		self.cxn.commit()
		return token, 200

	def user_changeColor(self, color, user_id):
		color = color.removeprefix("#")
		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()

		if all(c in string.hexdigits for c in color):
			cursor.execute("UPDATE Users SET Color = %s WHERE ID = %s", (color, user_id))
			self.cxn.commit()
			return color, 200
		else:
			return "Invalid color value "+color, 400

	def user_logOut(self, token):
		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()

		cursor.execute("DELETE FROM Sessions WHERE Token = %s", (token,))
		self.cxn.commit()
		return "Goodbye", 200

	def users_new(self, username, email):
		alphabet = string.ascii_letters + string.digits
		password = ''.join(secrets.choice(alphabet) for i in range(20))
		hashed_password = util.hash(password)

		self.cxn.ping(reconnect=True)
		cursor = self.cxn.cursor()
		try:
			cursor.execute("INSERT INTO Users (Name, Email, HashedPass, Color) VALUES (%s, %s, %s, %s)", (username, email, hashed_password, "%06x" % randrange(16**6)))
			self.cxn.commit()
			return password, 200

		except IntegrityError:
			return "Username already in use", 400

M = Model()
