from PyQt5 import QtCore, QtWidgets


class ToolDetails(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, toolDetails):
        toolDetails.setObjectName("toolDetails")

        self.toolNameLabel = QtWidgets.QLabel(toolDetails)
        self.toolNameLabel.setGeometry(QtCore.QRect(270, 20, 101, 21))
        self.toolNameLabel.setLayoutDirection(QtCore.Qt.RightToLeft)  # type: ignore
        self.toolNameLabel.setObjectName("toolNameLabel")

        self.toolDescriptionLabel = QtWidgets.QLabel(toolDetails)
        self.toolDescriptionLabel.setGeometry(QtCore.QRect(270, 60, 101, 20))
        self.toolDescriptionLabel.setLayoutDirection(QtCore.Qt.RightToLeft)  # type: ignore
        self.toolDescriptionLabel.setObjectName("toolDescriptionLabel")

        self.inputSchemaLabel = QtWidgets.QLabel(toolDetails)
        self.inputSchemaLabel.setGeometry(QtCore.QRect(270, 140, 101, 20))
        self.inputSchemaLabel.setLayoutDirection(QtCore.Qt.RightToLeft)  # type: ignore
        self.inputSchemaLabel.setObjectName("inputSchemaLabel")

        self.functionCodeLabel = QtWidgets.QLabel(toolDetails)
        self.functionCodeLabel.setGeometry(QtCore.QRect(270, 470, 101, 20))
        self.functionCodeLabel.setLayoutDirection(QtCore.Qt.RightToLeft)  # type: ignore
        self.functionCodeLabel.setObjectName("functionCodeLabel")

        self.apiKeyLabel = QtWidgets.QLabel(toolDetails)
        self.apiKeyLabel.setGeometry(QtCore.QRect(270, 710, 91, 20))
        self.apiKeyLabel.setLayoutDirection(QtCore.Qt.RightToLeft)  # type: ignore
        self.apiKeyLabel.setObjectName("apiKeyLabel")

        self.toolNameLineEdit = QtWidgets.QLineEdit(toolDetails)
        self.toolNameLineEdit.setGeometry(QtCore.QRect(380, 20, 331, 25))
        self.toolNameLineEdit.setObjectName("toolNameLineEdit")

        self.toolDescriptionTextEdit = QtWidgets.QTextEdit(toolDetails)
        self.toolDescriptionTextEdit.setGeometry(QtCore.QRect(380, 60, 331, 70))
        self.toolDescriptionTextEdit.setObjectName("toolDescriptionTextEdit")

        self.inputSchemaTableView = QtWidgets.QTableView(toolDetails)
        self.inputSchemaTableView.setGeometry(QtCore.QRect(380, 140, 331, 311))
        self.inputSchemaTableView.setLayoutDirection(QtCore.Qt.LeftToRight)  # type: ignore
        self.inputSchemaTableView.setObjectName("inputSchemaTableView")

        self.apiLineEdit = QtWidgets.QLineEdit(toolDetails)
        self.apiLineEdit.setGeometry(QtCore.QRect(380, 700, 331, 25))
        self.apiLineEdit.setObjectName("apiLineEdit")

        self.toolFunctionTextEdit = QtWidgets.QPlainTextEdit(toolDetails)
        self.toolFunctionTextEdit.setGeometry(QtCore.QRect(380, 460, 331, 231))
        self.toolFunctionTextEdit.setObjectName("toolFunctionTextEdit")

        self.addSchemaPushButton = QtWidgets.QPushButton(toolDetails)
        self.addSchemaPushButton.setGeometry(QtCore.QRect(280, 170, 80, 25))
        self.addSchemaPushButton.setObjectName("addSchemaPushButton")

        self.removeSchemaPushButton = QtWidgets.QPushButton(toolDetails)
        self.removeSchemaPushButton.setGeometry(QtCore.QRect(280, 200, 80, 25))
        self.removeSchemaPushButton.setObjectName("removeSchemaPushButton")

        self.editToolPushButton = QtWidgets.QPushButton(toolDetails)
        self.editToolPushButton.setGeometry(QtCore.QRect(540, 730, 80, 25))
        self.editToolPushButton.setObjectName("editToolPushButton")

        self.saveToolPushButton = QtWidgets.QPushButton(toolDetails)
        self.saveToolPushButton.setGeometry(QtCore.QRect(630, 730, 80, 25))
        self.saveToolPushButton.setObjectName("saveToolPushButton")

    def setToolDetails(self, tool):
        self.toolNameLineEdit.setText(tool.name)
        self.toolDescriptionTextEdit.setText(tool.description)
        self.inputSchemaTableView.setModel(tool.inputSchema)
        self.apiLineEdit.setText(tool.apiKey)
        self.toolFunctionTextEdit.setPlainText(tool.functionCode)

    def getToolDetails(self):
        # Implement logic to retrieve tool details from the UI and return a Tool object
        pass

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.toolNameLabel.setText(_translate("ToolDetails", "Tool Name:"))
        self.toolDescriptionLabel.setText(
            _translate("ToolDetails", "Tool Description:")
        )
        self.inputSchemaLabel.setText(_translate("ToolDetails", "Input Schema:"))
        self.functionCodeLabel.setText(_translate("ToolDetails", "Function Code:"))
        self.apiKeyLabel.setText(_translate("ToolDetails", "API Key:"))

        # Additionally, update the button texts and tooltips if they have text.
        self.addSchemaPushButton.setText(_translate("ToolDetails", "+"))
        self.addSchemaPushButton.setToolTip(
            _translate("ToolDetails", "Add a field to the schema")
        )
        self.removeSchemaPushButton.setText(_translate("ToolDetails", "-"))
        self.removeSchemaPushButton.setToolTip(
            _translate("ToolDetails", "Remove selected field from the schema")
        )
        self.editToolPushButton.setText(_translate("ToolDetails", "Edit"))
        self.saveToolPushButton.setText(_translate("ToolDetails", "Save"))
