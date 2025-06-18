from abc import ABC, abstractmethod


class KeyManagementInterface(ABC):
    """
    An abstract base class defining the interface for key management systems.

    This class provides an interface for storing and retrieving secrets (e.g., API keys) securely.
    Subclasses should implement the `store_secret` and `retrieve_secret` methods according to their
    specific key management system.

    Methods:
        store_secret(key: str, value: str) -> None:
            Stores the given secret value associated with the specified key.

        retrieve_secret(key: str) -> str:
            Retrieves the secret value associated with the specified key.
    """

    @abstractmethod
    def store_secret(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def retrieve_secret(self, key: str) -> str:
        pass
