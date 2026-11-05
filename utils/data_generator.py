# utils/data_generator.py
import uuid

from faker import Faker

fake = Faker("en_US")


class DataGenerator:

    @staticmethod
    def generate_email():
        # uuid4 гарантирует уникальность даже на общем стенде - приём из Темы 8
        return f"student-{uuid.uuid4().hex[:8]}@example.com"

    @staticmethod
    def generate_password():
        return fake.password(length=12)

    @staticmethod
    def generate_full_name():
        return fake.name()

    @staticmethod
    def generate_phone():
        return fake.phone()

    @staticmethod
    def generate_sku():
        return uuid.uuid4().hex

    @staticmethod
    def generate_description():
        return fake.sentence()

    @staticmethod
    def generate_price() -> int:
        return fake.random_int(min=100, max=50000)

    @staticmethod
    def generate_stock() -> int:
        return fake.random_int(min=10, max=100)

    @staticmethod
    def generate_uuid():
        return uuid.uuid4().hex