# tests/products/test_products.py
from decimal import Decimal
from itertools import product
from urllib import response
from venv import create
from wsgiref.util import application_uri
import uuid
from utils.data_generator import DataGenerator

class TestProducts:

    def test_get_products_returns_paginated_catalog(self, api_manager):
        response = api_manager.products_api.get_products()

        data = response.json()
        assert data["total"] > 0
        assert len(data["items"]) <= data["size"]

    def test_products_price_filter(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"price_min": 5000, "size": 100}
        )

        products = response.json()["items"]
        assert products, "Ожидали хотя бы один товар дороже 5000"
        for product in products:
            # цена приходит строкой - деньги сравниваем через Decimal (Тема 8)
            assert Decimal(product["price"]) >= 5000

    def test_get_product_id(self, api_manager):
        products = api_manager.products_api.get_products().json()["items"]
        product_id = products[0]["id"]

        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    def test_get_wrong_product_id(self, api_manager):
        product_id = uuid.uuid4()

        response = api_manager.products_api.get_product(product_id, expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_create_product(self, api_manager, authenticated_admin):
        payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
        }

        response = api_manager.products_api.create_product(payload=payload, expected_status=201)

        try:
            assert response.json()["name"] == payload["name"]
            assert response.json()["sku"] == payload["sku"]
            assert response.json()["description"] == payload["description"]
        finally:
            api_manager.products_api.delete_product(response.json()["id"])

    def test_update_product(self, api_manager, created_product):
        product_id = created_product["id"]
        payload = {
            "name": DataGenerator.generate_full_name()
        }

        response = api_manager.products_api.update_product(product_id, payload, expected_status=200)

        assert Decimal(response.json()["price"]) == Decimal(
            str(created_product["price"])
        )
        assert response.json()["sku"] == created_product["sku"]
        assert response.json()["description"] == created_product["description"]
        assert response.json()["name"] == payload["name"]
        assert api_manager.products_api.get_product(product_id).json()["name"] == payload["name"]

    def test_update_price(self, api_manager, created_product):
        product_id = created_product["id"]
        payload = {
            "price": 3000
        }

        response = api_manager.products_api.update_price(product_id, payload, expected_status=200)
        price_decimal = Decimal(api_manager.products_api.get_product(product_id).json()["price"])

        assert Decimal(response.json()["price"]) == payload["price"]
        assert response.json()["sku"] == created_product["sku"]
        assert response.json()["description"] == created_product["description"]
        assert price_decimal == payload["price"]

    def test_delete_product(self, api_manager, authenticated_admin):
        payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
        }

        response_create = api_manager.products_api.create_product(
            payload=payload, expected_status=201
        )
        product_id = response_create.json()["id"]
        response_delete = api_manager.products_api.delete_product(
            response_create.json()["id"]
        )
        deleted_product_response = api_manager.products_api.get_product(
            product_id,
            expected_status=200,
        )

        assert deleted_product_response.json()["id"] == product_id
        assert deleted_product_response.json()["is_available"] is False

    def test_user_cannot_create_product(self, api_manager, authenticated_user):
        payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
        }

        response = api_manager.products_api.create_product(payload=payload, expected_status=403)

        assert response.json()["error"]["code"] == "FORBIDDEN"

    def test_token_missing_create_product(self, api_manager):
        payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
        }

        response = api_manager.products_api.create_product(payload=payload, expected_status=401)

        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_exist_sku_create_product(self, api_manager, created_product):
        payload = {
            "name": DataGenerator.generate_full_name(),
            "sku": created_product["sku"],
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": api_manager.categories_api.get_categories().json()[0]["id"]
        }

        response = api_manager.products_api.create_product(payload=payload, expected_status=409)

        assert response.json()["error"]["code"] == "SKU_EXISTS"

    def test_not_found_category(self, api_manager, created_product):
        product_id = created_product["id"]
        payload = {
            "category_id": DataGenerator.generate_uuid()
        }

        response = api_manager.products_api.update_product(product_id, payload, expected_status=404)

        assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"

    def test_update_price_with_zero(self, api_manager, created_product):
        product_id = created_product["id"]
        payload = {
            "price": 0
        }

        response = api_manager.products_api.update_price(
            product_id, payload, expected_status=422
        )
        details = response.json()["detail"]

        assert any(error["loc"][-1] == "price" for error in details)

    def test_get_products_item_id(self, api_manager, created_product):
        params = {
            "category_id": created_product["category_id"]
        }
        response = api_manager.products_api.get_products(
            params=params, expected_status=200
        )

        products = response.json()["items"]

        assert products
        for product in products:
            assert product["category_id"] == created_product["category_id"]

    def test_get_products_returns_different_pages(self, api_manager):
        page_size = 2

        first_response = api_manager.products_api.get_products(
            params={"page": 1, "size": page_size},
        )

        second_response = api_manager.products_api.get_products(
            params={"page": 2, "size": page_size},
        )

        first_data = first_response.json()
        second_data = second_response.json()
        first_items = first_data["items"]
        second_items = second_data["items"]

        assert first_data["total"] > page_size
        assert len(first_items) <= page_size
        assert len(second_items) <= page_size

        first_ids = {product["id"] for product in first_items}
        second_ids = {product["id"] for product in second_items}

        assert first_ids.isdisjoint(second_ids)


    def