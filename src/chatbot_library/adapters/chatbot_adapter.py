from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# Avoid circular imports by using TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.conversation_dataclasses import Message, Response
    from ..tools.compatibility import Tool


@dataclass
class ChatbotCapabilities:
    """
    Represents the capabilities of a chatbot.

    Attributes:
        function_calling (bool): Indicates if the chatbot supports function calling.
        image_understanding (bool): Indicates if the chatbot supports image understanding.
        supported_images (list[str]): A list of supported image types.
    """

    function_calling: bool = False
    image_understanding: bool = False
    supported_images: list[str] = field(default_factory=list)


@dataclass
class ChatbotParameters:
    """
    Represents the parameters for a chatbot.

    Attributes:
        model_name (str): The name of the chatbot model.
        system_message (str): The system message to initialize the chatbot.
        max_tokens (int): The maximum number of tokens allowed in a response.
        stop_sequences (list[str]): A list of stop sequences to terminate the response generation.
        temperature (float): The temperature value for controlling response randomness.
        tools (list[Tool]): A list of available tools for the chatbot.
        capabilities (ChatbotCapabilities): The capabilities of the chatbot.
    """

    model_name: str
    display_name: str
    system_message: str
    max_tokens: int
    stop_sequences: list[str]
    temperature: float
    tools: list
    capabilities: ChatbotCapabilities


class ChatbotAdapter(ABC):
    """
    Abstract base class for chatbot adapters.

    Attributes:
        parameters (ChatbotParameters): The parameters for the chatbot.

    Methods:
        send_message_with_tools(messages: list[Message], active_tools: list[Tool]) -> Response:
            Sends a message to the chatbot with active tools and returns the response.

        send_message_without_tools(messages: list[Message]) -> Response:
            Sends a message to the chatbot without tools and returns the response.

        supported_models() -> list[str]:
            Returns a list of supported models by the chatbot.

        models_supporting_tools() -> list[str]:
            Returns a list of models that support function calling.

        models_supporting_image_understanding() -> list[str]:
            Returns a list of models that support image understanding.

        supports_function_calling() -> bool:
            Checks if the chatbot supports function calling.

        supports_image_understanding() -> bool:
            Checks if the chatbot supports image understanding.

        supported_images() -> list[str]:
            Returns a list of supported image types by the chatbot.
    """

    def __init__(self, parameters: ChatbotParameters) -> None:
        """
        Initializes a new instance of the ChatbotAdapter class.

        Args:
            parameters (ChatbotParameters): The parameters for the chatbot.
        """
        self.parameters = parameters

    @abstractmethod
    def send_message_with_tools(
        self, messages: list, active_tools: list
    ):
        """
        Sends a message to the chatbot with active tools and returns the response.

        Args:
            messages (list[Message]): The list of messages to send to the chatbot.
            active_tools (list[Tool]): The list of active tools available to the chatbot.
            branch_id (int): The branch id of the message being responded to.

        Returns:
            Response: The response from the chatbot.
        """
        pass

    @abstractmethod
    def send_message_without_tools(self, messages: list):
        """
        Sends a message to the chatbot without tools and returns the response.

        Args:
            messages (list[Message]): The list of messages to send to the chatbot.

        Returns:
            Response: The response from the chatbot.
        """
        pass

    @staticmethod
    @abstractmethod
    def supported_models() -> list[str]:
        """
        Returns a list of supported models by the chatbot.

        Returns:
            list[str]: The list of supported models.
        """
        pass

    @staticmethod
    @abstractmethod
    def models_supporting_tools() -> list[str]:
        """
        Returns a list of models that support function calling.

        Returns:
            list[str]: The list of models that support function calling.
        """
        pass

    @staticmethod
    @abstractmethod
    def models_supporting_image_understanding() -> list[str]:
        """
        Returns a list of models that support image understanding.

        Returns:
            list[str]: The list of models that support image understanding.
        """
        pass

    def display_name(self) -> str:
        return self.parameters.display_name

    def supports_function_calling(self) -> bool:
        """
        Checks if the chatbot supports function calling.

        Returns:
            bool: True if the chatbot supports function calling, False otherwise.
        """
        return self.parameters.capabilities.function_calling

    def supports_image_understanding(self) -> bool:
        """
        Checks if the chatbot supports image understanding.

        Returns:
            bool: True if the chatbot supports image understanding, False otherwise.
        """
        return self.parameters.capabilities.image_understanding

    def supported_images(self) -> list[str]:
        """
        Returns a list of supported image types by the chatbot.

        Returns:
            list[str]: The list of supported image types.
        """
        return self.parameters.capabilities.supported_images
