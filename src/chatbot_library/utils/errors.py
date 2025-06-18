"""
ChatbotErrors
"""


class ChatbotError(Exception):
    pass


class MissingResponseError(ChatbotError):
    pass


class ModelNotSupportedError(ChatbotError):
    pass


class APIError(ChatbotError):
    pass


class InvalidRequestError(ChatbotError):
    pass


class AnthropicAPIError(ChatbotError):
    pass


class OpenAIAPIError(ChatbotError):
    pass


class InvalidMessageError(ChatbotError):
    def __init__(self, message, json_content):
        super().__init__(message)
        self.json_content = json_content


class InvalidAPIClientError(ChatbotError):
    pass


"""
ConversationManagerErrors
"""


class ConversationManagerError(Exception):
    pass


class ChatbotNotFoundError(ConversationManagerError):
    pass


class ConversationStoreNotFoundError(ConversationManagerError):
    pass


class ConversationNotFoundError(ConversationManagerError):
    pass


class BranchNotFoundError(ConversationManagerError):
    pass


class MessageNotFoundError(ConversationManagerError):
    pass


class InvalidConversationDataError(ConversationManagerError):
    pass


class SaveConversationError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

    def format_error_message(self):
        error_message = str(self)
        if self.error_code == "NO_BRANCHES":
            hint = "Hint: Make sure to create at least one branch before saving the conversation."
        elif self.error_code == "UNEXPECTED_ERROR":
            hint = "Hint: Check the conversation data and ensure it is properly structured."
        elif self.error_code == "FILE_WRITE_ERROR":
            hint = "Hint: Check if the conversation directory exists and if you have write permissions."
        else:
            hint = "Hint: Review the conversation data and ensure it meets the expected format."
        return f"{error_message}\n{hint}"
