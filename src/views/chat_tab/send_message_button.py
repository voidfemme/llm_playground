from PyQt5 import QtCore, QtWidgets


class SendMessageButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, sendMessagePushButton):
        sendMessagePushButton.setGeometry(QtCore.QRect(710, 730, 231, 91))
        sendMessagePushButton.setObjectName("sendMessagePushButton")

    def retranslateUi(self, sendMessagePushButton):
        _translate = QtCore.QCoreApplication.translate
        sendMessagePushButton.setText(_translate("MainWindow", "Send"))

    def connectClicked(self, slot):
        self.clicked.connect(slot)
