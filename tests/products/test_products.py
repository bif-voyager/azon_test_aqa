# tests/products/test_products.py
from decimal import Decimal
from urllib import response
from wsgiref.util import application_uri
import uuid

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