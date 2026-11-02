import pytest
import requests

from api.api_manager import ApiManager
from api.categories_api import CategoriesAPI
from data.users import UserData
from utils.data_generator import DataGenerator


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

@pytest.fixture
def registered_admin(api_manager):
    user_data = UserData.registration_data_admin()
    response = api_manager.auth_api.register_user(user_data)

    return {**user_data, "id": response.json()["id"]}

@pytest.fixture
def registered_manager(api_manager):
    user_data = UserData.registration_data_manager()
    response = api_manager.auth_api.register_user(user_data)

    return {**user_data, "id": response.json()["id"]}

@pytest.fixture
def authenticated_admin(api_manager):
    admin_data = UserData.registration_data_admin()
    response = api_manager.auth_api.register_user(admin_data)

    api_manager.auth_api.authenticate((admin_data["email"], admin_data["password"]))

    return {**admin_data, "id": response.json()["id"]}

@pytest.fixture
def authenticated_manager(api_manager):
    manager_data = UserData.registration_data_manager()
    response = api_manager.auth_api.register_user(manager_data)

    api_manager.auth_api.authenticate((manager_data["email"], manager_data["password"]))

    return {**manager_data, "id": response.json()["id"]}

@pytest.fixture
def created_product(api_manager, authenticated_admin):
    payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": 49999.9,
            "stock": 100,
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
    }

    response = api_manager.products_api.create_product(payload=payload, expected_status=201)

    created_product_data = {**payload, "id": response.json()["id"]}

    yield created_product_data

    api_manager.products_api.delete_product(created_product_data["id"])