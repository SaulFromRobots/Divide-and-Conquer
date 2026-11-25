"""List queries for routes/lists.py.

Stubs for now: the real code comes in Phase 3, after schema version 2,
and the names and inputs below won't change. Every function returns plain
Python data, and the route decides the HTTP status code. The routes check
access first, with members.member_role(), before they call these.
"""


def lists_of_user(user_id):
	"""Return every list the user is a member of, as owner or collaborator.

	Returns a list of dicts with the keys ID and Name, sorted by ID, for
	example [{"ID": 3, "Name": "Groceries"}]. A user with no lists gets [].
	"""
	raise NotImplementedError


def list_get(list_id):
	"""Return one list as a dict, or None if there is no list with that ID.

	The dict has the keys ID, Name, Owners, and Collaborators, like the Lists
	table in our spec. Owners and Collaborators are lists of user IDs.
	"""
	raise NotImplementedError


def list_create(user_id, name):
	"""Create a list called name, with the user as its owner.

	Returns the new list's ID. The list and its owner are saved together in
	one transaction: if one fails, neither is saved.
	"""
	raise NotImplementedError


def list_rename(list_id, name):
	"""Change a list's name.

	Returns True, or False if there is no list with that ID.
	"""
	raise NotImplementedError


def list_delete(list_id):
	"""Delete a list, together with its tasks and its members.

	Returns True, or False if there is no list with that ID.
	"""
	raise NotImplementedError
