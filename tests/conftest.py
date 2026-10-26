import pytest
import requests

from api.api_manager import ApiManager
from data.users import UserData


@pytest.fixture(scope="session")
def api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()


@pytest.fixture
def registered_user(api_manager):
    user_data = UserData.registration_data()
    response = api_manager.auth_api.register_user(user_data)

    return {**user_data, "id": response.json()["id"]}

@pytest.fixture
def authenticated_user(api_manager):
    user_data = UserData.registration_data()
    response = api_manager.auth_api.register_user(user_data)

    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))

    return {**user_data, "id": response.json()["id"]}
@pytest.fixture(autouse=True)
def api_manager_clear(api_manager):
    yield
    api_manager.session.headers.pop("Authorization", None)