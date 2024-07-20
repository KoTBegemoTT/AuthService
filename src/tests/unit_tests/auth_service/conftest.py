import pytest

from app.auth_service.views import users


@pytest.fixture(autouse=True)
def setup():
    users.clear()
