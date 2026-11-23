"""Everything in the team plan's "Already built" table must still work after the split."""


def sign_up(client, username="alice", email="alice@example.com"):
	return client.post("/users/new", data={"username": username, "email": email})


def log_in(client, username, password):
	return client.post("/user/login", data={"username": username, "password": password})


def test_sign_up_returns_a_new_password(client):
	response = sign_up(client)
	assert response.status_code == 200
	assert len(response.get_data(as_text=True)) == 20


def test_duplicate_username_is_rejected(client):
	sign_up(client)
	response = sign_up(client, email="other@example.com")
	assert response.status_code == 400


def test_missing_field_is_rejected(client):
	response = client.post("/users/new", data={"username": "bob"})
	assert response.status_code == 400


def test_wrong_password_is_rejected(client):
	sign_up(client)
	response = log_in(client, "alice", "wrong-password")
	assert response.status_code == 401


def test_log_in_sets_a_token_and_goes_home(client):
	password = sign_up(client).get_data(as_text=True)
	response = log_in(client, "alice", password)
	assert response.status_code == 302
	assert response.headers["Location"] == "/"
	assert "token=" in response.headers["Set-Cookie"]


def test_home_page_shows_the_logged_in_user(client):
	password = sign_up(client).get_data(as_text=True)
	log_in(client, "alice", password)
	response = client.get("/")
	assert b"Logged in as user ID #1" in response.data


def test_change_color(client, query):
	password = sign_up(client).get_data(as_text=True)
	log_in(client, "alice", password)
	response = client.post("/user/changeColor", data={"color": "#ff0000"})
	assert response.status_code == 200
	assert query("SELECT Color FROM Users WHERE Name = %s", ("alice",))[0][0] == "ff0000"


def test_change_color_needs_a_login(client):
	response = client.post("/user/changeColor", data={"color": "#123456"})
	assert response.status_code == 401


def test_log_out_ends_the_session(client, query):
	password = sign_up(client).get_data(as_text=True)
	cookie = log_in(client, "alice", password).headers["Set-Cookie"]
	old_token = cookie.split("token=", 1)[1].split(";", 1)[0]

	response = client.post("/user/logOut")
	assert response.status_code == 200
	assert query("SELECT COUNT(*) FROM Sessions")[0][0] == 0

	# The old token must not work anymore.
	client.set_cookie("token", old_token)
	assert client.post("/user/changeColor", data={"color": "#123456"}).status_code == 401


def test_session_expires_after_30_minutes(client, query):
	password = sign_up(client).get_data(as_text=True)
	log_in(client, "alice", password)
	query("UPDATE Sessions SET LastUsed = NOW() - INTERVAL 31 MINUTE")
	assert b"Logged in as" not in client.get("/").data
