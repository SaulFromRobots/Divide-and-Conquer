"""User and session queries, moved from model.py without changing behavior.

Each function gets this request's connection from get_db() instead of
sharing one connection, so ping(reconnect=True) is no longer needed.
"""
# https://realpython.com/python-sql-libraries
import secrets
import string
from random import randrange

from mysql.connector.errors import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

SESSION_EXPIRE_MINUTES = 30

# If the token passed to the function is non-stale and exists, return the user ID associated with it. Otherwise return an error message.
def user_of_token(token):
	db = get_db()
	cursor = db.cursor()

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
	db.commit()
	return resp

# All further functions perform actions corresponding to API endpoints

def user_login(username, password):
	db = get_db()
	cursor = db.cursor()

	cursor.execute("SELECT HashedPass, ID FROM Users WHERE Name = %s", (username,))
	try:
		[hashed_pass,user_id] = cursor.fetchall()[0]
		if not check_password_hash(hashed_pass, password):
			raise ValueError
	except:
		return "Bad username/password combination", 401

	token = secrets.token_urlsafe(192)

	cursor.execute("INSERT INTO Sessions (UserID, Token, LastUsed) VALUES (%s, %s, NOW())", (user_id, token))
	db.commit()
	return token, 200

def user_changeColor(color, user_id):
	color = color.removeprefix("#")
	db = get_db()
	cursor = db.cursor()

	if all(c in string.hexdigits for c in color):
		cursor.execute("UPDATE Users SET Color = %s WHERE ID = %s", (color, user_id))
		db.commit()
		return color, 200
	else:
		return "Invalid color value "+color, 400

def user_logOut(token):
	db = get_db()
	cursor = db.cursor()

	cursor.execute("DELETE FROM Sessions WHERE Token = %s", (token,))
	db.commit()
	return "Goodbye", 200

def users_new(username, email):
	alphabet = string.ascii_letters + string.digits
	password = ''.join(secrets.choice(alphabet) for i in range(20))
	hashed_password = generate_password_hash(password)

	db = get_db()
	cursor = db.cursor()
	try:
		cursor.execute("INSERT INTO Users (Name, Email, HashedPass, Color) VALUES (%s, %s, %s, %s)", (username, email, hashed_password, "%06x" % randrange(16**6)))
		db.commit()
		return password, 200

	except IntegrityError:
		return "Username already in use", 400
