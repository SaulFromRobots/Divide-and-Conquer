from enum import Enum

"""List member queries for routes/members.py and the access checks.

Stubs for now: the real code comes in Phase 3, after schema version 2,
and the names and inputs below won't change. Every function returns plain
Python data, and the route decides the HTTP status code.

A member has one of two roles, "Owner" or "Colab" (collaborator), the same
words as the MembershipChanges table in our spec. A list always keeps at
least one owner.
"""

ROLES = Enum("Role", [("Owner",1), ("Colab",2)])

def member_role(list_id, user_id):
	"""Return the user's role in a list: "Owner", "Colab", or None.

	None means the user is not a member, or there is no such list. Every list
	route checks this first (directly, or through the list-member check in
	security.py), to decide whether the logged-in user may go on.
	"""
	raise NotImplementedError


def members_of_list(list_id):
	"""Return a list's members, grouped by role.

	Returns {"Owners": [...], "Collaborators": [...]}, where each user is a
	dict with the keys ID, Name, and Color.
	"""
	raise NotImplementedError


def member_add(list_id, username, role="Colab"):
	"""Add a user to a list, by username, with the given role.

	Returns "added", "no_such_user", or "already_member". An existing
	member's role doesn't change here; use member_set_role for that.
	"""
	raise NotImplementedError


def member_set_role(list_id, username, role):
	"""Change a member's role to "Owner" or "Colab".

	Returns "changed", "no_such_user", "not_member", or "last_owner". With
	"last_owner", nothing changed, because the list would have no owner left.
	"""
	raise NotImplementedError


def member_remove(list_id, username):
	"""Remove a user from a list. Their tasks in that list become unassigned.

	Returns "removed", "no_such_user", "not_member", or "last_owner". With
	"last_owner", nothing changed, because they are the list's only owner.
	"""
	raise NotImplementedError
