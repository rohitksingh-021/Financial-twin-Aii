"""In-memory data store for customer data. Thread-safe singleton."""

import threading
from models.customer import CustomerData
from seed.rahul_sharma import get_seed_data


class DataStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = get_seed_data()
        return cls._instance

    def get_customer(self) -> CustomerData:
        return self._data

    def set_customer(self, data: CustomerData) -> None:
        with self._lock:
            self._data = data

    def reset(self) -> None:
        with self._lock:
            self._data = get_seed_data()


store = DataStore()
