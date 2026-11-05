from utils.data_generator import DataGenerator

class ProductData:

    @staticmethod
    def create_product_data(category_id) -> dict:
        return {
            "name": DataGenerator.generate_full_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": category_id
        }
