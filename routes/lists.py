"""The /lists/... routes."""

from __init__ import ensure_args
from flask import Blueprint, jsonify, request

from models import items, lists, members, users

bp = Blueprint("lists", __name__)

# TODO: use members.member_role(list_id, user_id) instead of concating two lists from the_list every time
	# NOTE: member_role requires user_id while some of the methods that ought to use it only have `username`

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
		jsonify(lists.list_create(value, "New list"))

@bp.route("/<int:list_id>", methods=["GET"])
def lists_id():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	if not worked:
		return value, 401
	else:
		the_list = lists.list_get(request.args.get("list_id"))
		if the_list is None:
			return "Nonexistant list", 400
		elif value in the_list["Owners"] ++ the_list["Collaborators"]:
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
			return 200 if lists.list_delete(list_id) else (400, "Nonexistant list")
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
			return 200 if lists.list_rename(list_id, request.form["name"]) else (400, "Nonexistant list")
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
			return jsonify(items.item_create(list_id, ""))
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:item_id>", methods=["GET"])
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
			the_item = items.item_get(list_id, item_id)
			return the_item if the_item is not None else ("Nonexistant item", 400)
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:item_id>", methods=["PATCH"])
@ensure_args(["text","assignee","state"])
def lists_id_items_id_patch():
	token = request.cookies.get("token")
	value, worked = users.user_of_token(token)

	list_id = request.args.get("list_id")
	item_id = request.args.get("item_id")
	if not worked:
		return value, 401
	else:
		the_list = lists.list_get(list_id)
		if value in the_list["Owners"] ++ the_list["Collaborators"]:
			assignee = request.form["assignee"]
			if assignee is None or assignee in the_list["Owners"] ++ the_list["Collaborators"]:
				try:
					state = items.STATES(request.form["state"])
				except ValueError:
					return "Invalid state", 400
				return 200 if items.item_update(list_id, item_id, request.form["text"], assignee, state) else (400, "Nonexistant item")
			else:
				return "Assignee does not have access to the requested list", 403
		else:
			return "User does not have access to the requested list", 403

@bp.route("/<int:list_id>/items/<int:item_id>", methods=["DELETE"])
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
			return 200 if items.item_delete(list_id, item_id) else (400, "Nonexistant item")
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

	if not worked:
		return value, 401
	else:
		list_id = request.args.get("list_id")
		the_list = lists.list_get(list_id)
		if value in the_list["Owners"]:
			match members.member_add(list_id, request.form["username"]):
				case "added": return 200
				case "no_such_user": return "Nonexistant user", 400
				case "already_member": return "User is already a member of the list", 400
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
			match members.member_set_role(list_id, promoted_username, members.ROLES.Owner):
				case "changed" | "last_owner": return 200
				case "no_such_user": return "Nonexistant user", 400
				case "not_member":
					match members.member_add(list_id, request.form["username"]):
						case "added": return 200
						case "no_such_user": return "Nonexistant user", 400
						case "already_member": return "THIS SHOULD NEVER HAPPEN", 500
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
			match members.member_remove(list_id, removed_username):
				case "removed": return 200
				case "no_such_user" | "not_member": return "User is not a member of the list", 400
				case "last_owner": return "That's the last owner of the list", 400
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
			match members.member_set_role(list_id, demoted_username, members.ROLES.Colab):
				case "changed": return 200
				case "not_member" | "no_such_user": return "User is not a member of the list", 400
				case "last_owner": return "That's the last owner of the list", 400
		else:
			return "User is not Owner of the requested list", 403
