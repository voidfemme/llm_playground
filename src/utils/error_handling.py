"""
ChatbotErrors
"""


class ChatbotError(Exception):
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
    pass


"""
ConversationManagerErrors
"""


class ConversationManagerError(Exception):
    pass


class ConversationNotFoundError(ConversationManagerError):
    pass


class BranchNotFoundError(ConversationManagerError):
    pass


class MessageNotFoundError(ConversationManagerError):
    pass


class InvalidConversationDataError(ConversationManagerError):
    pass
