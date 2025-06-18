import os
from key_management_interface import KeyManagementInterface


class EnvironmentVariableAdapter(KeyManagementInterface):
    def store_secret(self, key: str, value: str) -> None:
        raise NotImplementedError(
            "Storing secrets is not supported for envionment variables"
        )

    def retrieve_secret(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"Secret not found for key: {key}")
        return value
