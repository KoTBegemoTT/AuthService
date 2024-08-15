import pytest

from app.db.models import User


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {'name': 'user_1', 'password': b'password'}, id='user_1'),
        pytest.param({'name': 'admin', 'password': b'admin'},
                     id='username_equals_password'),
        pytest.param({'name': '', 'password': b''},
                     id='empty_username_and_password'),
    ],
)
def test_user_model(pyload):
    user = User(**pyload)
    assert user.name == pyload.get('name')
    assert user.password == pyload.get('password')


@pytest.mark.parametrize(
    'pyload, error_msg',
    [
        pytest.param(
            {'password': 'password'},
            "User.__init__() missing 1 required positional argument: 'name'",
            id='no_name'),
        pytest.param(
            {'name': 'user'},
            "User.__init__() missing 1 required positional argument: 'password'",  # noqa: E501
            id='no_password'),
    ],
)
def test_user_model_fail(pyload, error_msg):
    with pytest.raises(TypeError) as ex:
        User(**pyload)

    assert ex.value.args[0] == error_msg
