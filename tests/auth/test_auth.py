# tests/auth/test_auth.py
from data.users import UserData
from tests.payment.test_orders import authorized_user


class TestAuth:

    def test_register_and_login(self, api_manager):
        user_data = UserData.registration_data()

        register_response = api_manager.auth_api.register_user(user_data)
        assert register_response.json()["role"] == "USER"

        api_manager.auth_api.authenticate(UserData.login_data(user_data))

        me_response = api_manager.auth_api.get_me()
        assert me_response.json()["email"] == user_data["email"]

    def test_register_with_existing_email(self, api_manager, registered_user):
        response = api_manager.auth_api.register_user(registered_user, expected_status=409)
        assert response.json()["error"]["code"] == "EMAIL_EXISTS"

    def test_login_with_wrong_password(self, api_manager, registered_user):
        credentials = UserData.login_data(registered_user)
        credentials["password"] = "defenity-pass"
        response = api_manager.auth_api.login_user(credentials, expected_status=401)
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"