"""Schema version 2: the database itself rejects bad data (CS174-18, slides 40 and 44).

Each test tries one kind of bad data on dac_test and checks that MySQL
answers the way we planned: an error, a CASCADE, or SET NULL.
"""
import mysql.connector
import pytest

from models import items, members

# MySQL error numbers
FOREIGN_KEY_FAILS = 1452
DUPLICATE_KEY = 1062
PARENT_ROW_IN_USE = 1451
NOT_AN_ALLOWED_VALUE = 1265


def add_user(query, name):
	query("INSERT INTO Users (Name, Email, HashedPass, Color) VALUES (%s, %s, %s, %s)",
		(name, name + "@example.com", "x", "000000"))
	return query("SELECT ID FROM Users WHERE Name = %s", (name,))[0][0]


def add_list(query, name="Groceries"):
	query("INSERT INTO Lists (Name) VALUES (%s)", (name,))
	return query("SELECT MAX(ID) FROM Lists")[0][0]


def add_member(query, list_id, user_id, role="Colab"):
	query("INSERT INTO ListMembers (ListID, UserID, Role) VALUES (%s, %s, %s)",
		(list_id, user_id, role))


def add_task(query, list_id, text="Buy milk", assignee=None, order=0):
	query("INSERT INTO Items (ListID, Text, Assignee, OrderPlacement) VALUES (%s, %s, %s, %s)",
		(list_id, text, assignee, order))
	return query("SELECT MAX(ID) FROM Items")[0][0]


def error_number(run):
	"""Run the SQL and return MySQL's error number."""
	with pytest.raises(mysql.connector.Error) as caught:
		run()
	return caught.value.errno


def test_a_task_needs_a_real_list(query):
	assert error_number(lambda: add_task(query, list_id=999)) == FOREIGN_KEY_FAILS


def test_a_list_can_have_many_tasks(query):
	list_id = add_list(query)
	for n in range(20):
		add_task(query, list_id, order=n)
	assert query("SELECT COUNT(*) FROM Items WHERE ListID = %s", (list_id,))[0][0] == 20


def test_the_same_member_twice_is_rejected(query):
	list_id = add_list(query)
	henry = add_user(query, "Henry")
	add_member(query, list_id, henry, "Owner")
	assert error_number(lambda: add_member(query, list_id, henry, "Colab")) == DUPLICATE_KEY


def test_the_assignee_must_be_a_real_user(query):
	list_id = add_list(query)
	assert error_number(lambda: add_task(query, list_id, assignee=999)) == FOREIGN_KEY_FAILS


def test_the_database_accepts_a_non_member_assignee(query):
	# Option A: the database only checks "a real user."
	# The route must check "a member of this list" before it saves.
	list_id = add_list(query)
	outsider = add_user(query, "Outsider")
	add_task(query, list_id, assignee=outsider)
	assert query("SELECT Assignee FROM Items")[0][0] == outsider


def test_a_task_can_have_no_assignee(query):
	list_id = add_list(query)
	add_task(query, list_id, assignee=None)
	assert query("SELECT Assignee FROM Items")[0][0] is None


def test_a_state_outside_the_allowed_values_is_rejected(query):
	list_id = add_list(query)
	task_id = add_task(query, list_id)
	bad = lambda: query("UPDATE Items SET State = %s WHERE ID = %s", ("Finished", task_id))
	assert error_number(bad) == NOT_AN_ALLOWED_VALUE


def test_a_new_task_starts_as_no_progress(query):
	list_id = add_list(query)
	add_task(query, list_id)
	assert query("SELECT State FROM Items")[0][0] == "No progress"


def test_state_numbers_match_STATES(query):
	list_id = add_list(query)
	task_id = add_task(query, list_id)
	for state in items.STATES:
		query("UPDATE Items SET State = %s WHERE ID = %s", (state.value, task_id))
		assert query("SELECT State + 0 FROM Items WHERE ID = %s", (task_id,))[0][0] == state.value


def test_role_numbers_match_ROLES(query):
	list_id = add_list(query)
	henry = add_user(query, "Henry")
	add_member(query, list_id, henry, members.ROLES.Colab.value)
	assert query("SELECT Role FROM ListMembers")[0][0] == "Colab"


def test_deleting_a_list_deletes_its_tasks_and_members(query):
	list_id = add_list(query)
	henry = add_user(query, "Henry")
	add_member(query, list_id, henry, "Owner")
	add_task(query, list_id, assignee=henry)
	query("DELETE FROM Lists WHERE ID = %s", (list_id,))
	assert query("SELECT COUNT(*) FROM Items")[0][0] == 0
	assert query("SELECT COUNT(*) FROM ListMembers")[0][0] == 0
	assert query("SELECT COUNT(*) FROM Users")[0][0] == 1


def test_a_user_still_in_a_list_cannot_be_deleted(query):
	list_id = add_list(query)
	henry = add_user(query, "Henry")
	add_member(query, list_id, henry, "Owner")
	bad = lambda: query("DELETE FROM Users WHERE ID = %s", (henry,))
	assert error_number(bad) == PARENT_ROW_IN_USE


def test_deleting_a_user_unassigns_tasks_and_ends_sessions(query):
	list_id = add_list(query)
	outsider = add_user(query, "Outsider")
	add_task(query, list_id, assignee=outsider)
	query("INSERT INTO Sessions (UserID, Token, LastUsed) VALUES (%s, %s, NOW())", (outsider, "t" * 256))
	query("DELETE FROM Users WHERE ID = %s", (outsider,))
	assert query("SELECT Assignee FROM Items")[0][0] is None
	assert query("SELECT COUNT(*) FROM Sessions")[0][0] == 0


@pytest.mark.parametrize("first, second", [("Saul", "saul"), ("Saul", "SAUL"), ("José", "Jose")])
def test_usernames_ignore_case_and_accents(query, first, second):
	add_user(query, first)
	assert error_number(lambda: add_user(query, second)) == DUPLICATE_KEY
