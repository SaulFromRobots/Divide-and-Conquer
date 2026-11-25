"""The /lists/... routes."""

from __init__ import ensure_args
from flask import Blueprint, request

from models import items, lists, members, users

bp = Blueprint("lists", __name__)

# TODO: use members.member_role(list_id, user_id) instead of concating two lists from the_list every time
	# NOTE: member_role requires user_id while some of the methods that ought to use it only have `username`
# TODO: use the return values of the methods as documented in the methods documentation

@bp.route("/", methods=["GET"])
def lists_root():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	if not worked:
		return value, 401
	else:
		return lists.lists_of_user(value)

@bp.route("/new", methods=["POST"])
def lists_new():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	if not worked:
		return value, 401
	else:
		lists.list_create(value, "New list")

@bp.route("/<int:list_id>", methods=["GET"])
def lists_id():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	the_list = lists.list_get(request.args.get("list_id"))
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return the_list
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>", methods=["DELETE"])
def lists_id_delete():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"]:
			return lists.list_delete(list_id)
		else:
			return "User is not Owner of the requested list", 403

@bp.route("/<int:list_id>/rename", methods=["POST"])
@ensure_args(["name"])
def lists_id_rename():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return lists.list_rename(list_id, request.form["name"])
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items", methods=["GET"])
def lists_id_items():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return items.items_of_list(list_id)
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/new", methods=["POST"])
def lists_id_items_new():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return items.item_create(list_id, "")
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:list_id>", methods=["GET"])
def lists_id_items_id():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	item_id = request.args.get("item_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return items.item_get(list_id, item_id)
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:list_id>", methods=["PATCH"])
@ensure_args(["text","assignee","state"])
def lists_id_items_id_patch():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	item_id = request.args.get("item_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			assignee = request.form["assignee"]
			if assignee is None or assignee in the_list["Owners"] ++ the_list["Collaborators"]:
				try:
					state = items.STATES(request.form["state"])
				except ValueError:
					return "Invalid state", 400
				return items.item_update(list_id, item_id, request.form["text"], assignee, state)
			else:
				return "Assignee does not have access to the requested list", 403
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:list_id>", methods=["DELETE"])
def lists_id_items_id_delete():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	item_id = request.args.get("item_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] or value == items.item_get(list_id, item_id)["Assignee"]:
			return items.item_delete(list_id, item_id)
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/members", methods=["GET"])
def lists_id_members():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			return members.members_of_list(list_id)
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/members/add", methods=["POST"])
@ensure_args(["username"])
def lists_id_members_add():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"]:
			return members.member_add(list_id, request.form["username"])
		else:
			return "User is not Owner of the requested list", 403

@bp.route("/<int:list_id>/members/addOwner", methods=["POST"])
@ensure_args(["username"])
def lists_id_members_addOwner():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	promoted_username = request.form["username"]
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"]:
			if promoted_username in the_list["Collaborators"]:
				return members.member_set_role(list_id, promoted_username, members.ROLES.Owner)
			else:
				return members.member_add(list_id, promoted_username, members.ROLES.Owner)
		else:
			return "User is not Owner of the requested list", 403

@bp.route("/<int:list_id>/members/remove", methods=["POST"])
@ensure_args(["username"])
def lists_id_members_remove():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	removed_username = request.form["username"]
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"]:
			if removed_username in the_list["Collaborators"] ++ the_list["Owners"]:
				return members.member_remove(list_id, removed_username)
			else:
				return 200
		else:
			return "User is not Owner of the requested list", 403

@bp.route("/<int:list_id>/members/removeOwner", methods=["POST"])
@ensure_args(["username"])
def lists_id_members_removeOwner():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	the_list = lists.list_get(list_id)
	demoted_username = request.form["username"]
	if not worked:
		return value, 401
	else:
		if value in the_list["Owners"]:
			if demoted_username in the_list["Owners"]:
				return members.member_set_role(list_id, demoted_username, members.ROLES.Colab)
			else:
				return 200
		else:
			return "User is not Owner of the requested list", 403
