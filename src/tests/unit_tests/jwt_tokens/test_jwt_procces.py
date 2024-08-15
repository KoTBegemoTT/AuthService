import pytest

from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode
from app.db.models import User

pyload_without_name_params = [
    pytest.param({'some': 'payload'}, id='some_payload'),
    pytest.param({'password': 'password'}, id='only_password'),
    pytest.param({}, id='empty_payload'),
]


@pytest.mark.parametrize(
    'user',
    {
        pytest.param(User(name='user_1', password=b'password'), id='user_1'),
        pytest.param(User(name='admin', password=b'admin'),
                     id='username_equals_password'),
        pytest.param(User(name='', password=b''),
                     id='empty_username_and_password'),
    },
)
def test_jwt_encode(user):
    token = jwt_encode(user)
    assert isinstance(token, str)


@pytest.mark.parametrize(
    'user',
    {
        pytest.param(User(name='user_1', password=b'password'), id='user_1'),
        pytest.param(User(name='admin', password=b'admin'),
                     id='username_equals_password'),
        pytest.param(User(name='', password=b''),
                     id='empty_username_and_password'),
    },
)
def test_jwt_decode(user):
    token = jwt_encode(user)

    decode_data = jwt_decode(token)

    assert decode_data['username'] == user.name
    assert 'password' not in decode_data
    assert 'exp' in decode_data
    assert 'iat' in decode_data
