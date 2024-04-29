from PyQt5 import QtCore, QtWidgets


class SendMessageTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, sendMessageTextEdit):
        sendMessageTextEdit.setGeometry(QtCore.QRect(270, 700, 431, 131))
        sendMessageTextEdit.setObjectName("sendMessageTextEdit")

    def retranslateUi(self, sendMessageTextEdit):
        pass

    def getText(self):
        return self.toPlainText()

    def clearText(self):
        self.clear()
