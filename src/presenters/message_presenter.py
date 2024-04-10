# message_presenter.py

from typing import TYPE_CHECKING
from src.model.conversation_manager import Message
from src.utils.file_logger import LOG_FILE_PATH, log_function_call, log_variable
from src.views.message_widget import MessageWidget

if TYPE_CHECKING:
    from src.presenters.conversation_presenter import ConversationPresenter


class MessagePresenter:
    def __init__(self, conversation_presenter: "ConversationPresenter") -> None:
        self.conversation_presenter = conversation_presenter
        self.message_widgets = []

    def create_message_widget(
        self, message: Message, conversation_id: str, branch_id: str
    ) -> MessageWidget:
        log_function_call(
            LOG_FILE_PATH,
            "MessagePresenter.create_message_widget",
            message=message,
            conversation_id=conversation_id,
            branch_id=branch_id,
        )
        log_variable(LOG_FILE_PATH, "message", message)

        message_widget = MessageWidget(
            message, conversation_id, branch_id, self.conversation_presenter
        )
        message_widget.hamburger_menu.clicked.connect(  # type: ignore
            lambda: self.on_message_menu_clicked(message_widget)
        )
        message_widget.left_arrow.clicked.connect(
            lambda: self.on_left_arrow_clicked(message_widget)
        )
        message_widget.right_arrow.clicked.connect(
            lambda: self.on_right_arrow_clicked(message_widget)
        )
        self.message_widgets.append(message_widget)
        return message_widget

    def delete_message_widget(self, message_widget: MessageWidget) -> None:
        self.message_widgets.remove(message_widget)
        message_widget.deleteLater()

    def update_message_widgets(
        self, messages: list[Message], conversation_id: str, branch_id: str
    ) -> None:
        for message_widget in self.message_widgets:
            self.delete_message_widget(message_widget)

        for message in messages:
            self.create_message_widget(message, conversation_id, branch_id)

    def clear_message_widgets(self) -> None:
        for message_widget in self.message_widgets:
            self.delete_message_widget(message_widget)
        self.message_widgets.clear()

    def on_message_menu_clicked(self, message_widget: MessageWidget) -> None:
        # Handle message-level menu actions
        pass

    def on_left_arrow_clicked(self, message_widget: MessageWidget) -> None:
        # Handle left arrow click event
        pass

    def on_right_arrow_clicked(self, message_widget: MessageWidget) -> None:
        # Handle right arrow click event
        pass
