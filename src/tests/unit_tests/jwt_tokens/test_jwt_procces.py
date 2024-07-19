import pytest

from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode

pyload_valid_params = [
    pytest.param({'name': 'admin'}, id='only_name'),
    pytest.param(
        {'name': 'admin', 'password': 'password'},
        id='name_and_password'),
]

pyload_without_name_params = [
    pytest.param({'some': 'payload'}, id='some_payload'),
    pytest.param({'password': 'password'}, id='only_password'),
    pytest.param({}, id='empty_payload'),
]


class TestJwtProcess:
    @pytest.mark.parametrize('payload', pyload_valid_params)
    def test_jwt_encode(self, payload):
        token = jwt_encode(payload)
        assert isinstance(token, str)

    @pytest.mark.parametrize('payload', pyload_valid_params)
    def test_jwt_decode(self, payload):
        token = jwt_encode(payload)

        decode_data = jwt_decode(token)

        assert decode_data['name'] == payload['name']

    @pytest.mark.parametrize('payload', pyload_without_name_params)
    def test_jwt_encode_fail(self, payload):
        with pytest.raises(KeyError):
            jwt_encode(payload)
