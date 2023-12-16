# import pytest

# from core.deps import get_session
# from auth.auth import create_access_token, private_key
# from tests.test_main import session_fixture
# from tests.crud.test_crud_user import create_test_user
# from user.crud import user
# from utils.token_schema import TokenPayload
# import datetime

# def test_get_session():
#     session = get_session()
    
#     assert session is not None
    
# @pytest.fixture
# def token_fixture(create_test_user):
#     username, email, password = create_test_user
#     token_payload = TokenPayload(username=username, email=email, exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15))
#     token = create_access_token(token_payload, private_key)
#     return token
