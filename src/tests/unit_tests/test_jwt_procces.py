import pytest

from app.jwt_process import jwt_decode, jwt_encode

pyload_params = [
    pytest.param({'some': 'payload'}, id='some_payload'),
    pytest.param({'name': 'admin'}, id='only_name'),
    pytest.param({'password': 'password'}, id='only_password'),
    pytest.param(
        {'name': 'admin', 'password': 'password'},
        id='name_and_password'),
    pytest.param({}, id='empty_payload'),
]


class TestJwtProcess:
    @pytest.mark.parametrize('payload', pyload_params)
    def test_jwt_encode(self, payload):
        token = jwt_encode(payload)
        assert isinstance(token, str)

    @pytest.mark.parametrize('payload', pyload_params)
    def test_jwt_decode(self, payload):
        token = jwt_encode(payload)

        decode_data = jwt_decode(token)

        assert decode_data == payload
