import pytest

from app.logic import users


@pytest.fixture(autouse=True)
def setup():
    users.clear()
