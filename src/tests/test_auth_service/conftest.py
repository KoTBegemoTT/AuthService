import pytest
from app.logic import users
from app.models import User


@pytest.fixture(autouse=True)
def setup():
    users.clear()


@pytest.fixture
def add_user_1():
    useer = User(username="user_1", password="password")
    users[useer] = "token"

