"""Task (item) queries for routes/items.py.

Stubs for now: the real code comes in Phase 3, after schema version 2,
and the names and inputs below won't change. Every function returns plain
Python data, and the route decides the HTTP status code. The routes check
access first, with members.member_role(), before they call these.

A task is a dict with the keys ID, ListID, Text, Assignee (a user ID, or
None when nobody is assigned), State, and OrderPlacement. State is a STATES
member, for example STATES.NoProgress, not the words from the database.
Every function takes the list's ID too, so nobody can reach another list's
task by changing the URL.
"""
from enum import Enum

# The numbers match the order of the State enum in schema.sql.
STATES = Enum("State", [("NoProgress", 1), ("InProgress", 2), ("Done", 3)])

def items_of_list(list_id):
	"""Return every task in a list, sorted by OrderPlacement.

	Returns a list of task dicts, each with State as a STATES member.
	A list with no tasks gets [].
	"""
	raise NotImplementedError


def item_get(list_id, item_id):
	"""Return one task of a list, or None if that list has no such task.

	The task dict has State as a STATES member.
	"""
	raise NotImplementedError


def item_create(list_id, text, assignee=None):
	"""Add a task to the end of a list. Its State starts as STATES.NoProgress.

	assignee is a user ID, or None. The route checks first that the assignee
	is a member of the list (members.member_role).
	Returns the new task's ID.
	"""
	raise NotImplementedError


def item_update(list_id, item_id, text, assignee, state):
	"""Replace a task's Text, Assignee, and State.

	assignee is a user ID, or None. state is a STATES member, which the route
	makes from the client's number with items.STATES(number). The route checks
	first that the assignee is a member of the list.
	Returns True, or False if that list has no such task.
	"""
	raise NotImplementedError


def item_delete(list_id, item_id):
	"""Delete a task.

	Returns True, or False if that list has no such task.
	"""
	raise NotImplementedError
