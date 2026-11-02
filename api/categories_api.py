from requester.custom_requester import CustomRequester
from config.hosts import PRODUCT_URL

class CategoriesAPI(CustomRequester):

    CATEGORIES_ENDPOINT = "/api/v1/categories"

    def __init__(self, session):
        super().__init__(session, base_url=PRODUCT_URL)

    def get_categories(self, expected_status=200):
        return self.send_request(
            "GET",
            self.CATEGORIES_ENDPOINT,
            expected_status=expected_status
        )