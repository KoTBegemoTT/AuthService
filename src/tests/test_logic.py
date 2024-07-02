from app.logic import AuthService, users


def setup():
    users.clear()


def test_register():
    setup()
    AuthService.register("name", "password")

    assert len(users) == 1
    user = list(users.keys())[0]

    assert user.username == "name"
    assert user.password == "password"
    assert users[user] is not None


def test_login_success():
    setup()
    AuthService.register("name", "password")
    token = AuthService.login("name", "password")

    assert token is not None


def test_login_fail():
    setup()
    token = AuthService.login("name", "password")

    assert token is None
