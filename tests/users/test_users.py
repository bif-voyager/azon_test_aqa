from data.users import UserData
from utils.data_generator import DataGenerator

def test_get_user_info(api_manager, authenticated_user):
    response = api_manager.user_api.get_user_info()

    assert response.json()["id"] == authenticated_user["id"]
    assert response.json()["email"] == authenticated_user["email"]

def test_update_full_name(api_manager, authenticated_user):
    new_profile = UserData.update_profile_data()
    response = api_manager.user_api.update_user_info(new_profile)

    assert response.json()["full_name"] == new_profile["full_name"]
    assert api_manager.user_api.get_user_info().json()["full_name"] == new_profile["full_name"]

def test_change_password(api_manager, authenticated_user):
    new_password = DataGenerator.generate_password()

    api_manager.user_api.change_password(
        UserData.change_password_data(authenticated_user, new_password)
    )
    old_password = UserData.login_data(authenticated_user)

    response = api_manager.auth_api.login_user(old_password, expected_status=401)
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    api_manager.auth_api.authenticate((authenticated_user["email"], new_password))