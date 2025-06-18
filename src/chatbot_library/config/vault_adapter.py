import hvac

from .key_management_interface import KeyManagementInterface


class VaultAdapter(KeyManagementInterface):
    def __init__(self, vault_url, token) -> None:
        self.client = hvac.Client(url=vault_url, token=token)

    def store_secret(self, key: str, value: str) -> None:
        self.client.secrets.kv.v2.create_or_update_secret(
            path=key, secret={"value": value}
        )

    def retrieve_secret(self, key: str) -> str:
        secret = self.client.secrets.kv.v2.read_secret_version(path=key)
        return secret["data"]["data"]["value"]
