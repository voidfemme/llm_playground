from PyQt5 import QtCore, QtWidgets


class ActiveToolsList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.itemChanged.connect(
            self.handleItemChanged
        )  # Connect item changed signal to handler

    def setupUi(self, activeToolsListWidget):
        activeToolsListWidget.setGeometry(QtCore.QRect(0, 550, 261, 281))
        activeToolsListWidget.setObjectName("activeToolsListWidget")
        self.setAlternatingRowColors(True)  # Optional: for better UI visibility

    def addTool(self, tool_name):
        # Create a checkbox item
        item = QtWidgets.QListWidgetItem(self)
        checkbox = QtWidgets.QCheckBox(tool_name)
        checkbox.setCheckState(QtCore.Qt.Unchecked)  # Start unchecked  # type: ignore

        # Store the tool name in the item for identification
        item.setData(QtCore.Qt.UserRole, tool_name)  # type: ignore

        # Insert the checkbox into the list
        self.addItem(item)
        self.setItemWidget(item, checkbox)

    def removeTool(self, tool_name):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.text() == tool_name:
                self.takeItem(self.row(item))
                break

    def clearTools(self):
        self.clear()

    def handleItemChanged(self, item):
        # Handle the item check state change if needed
        checkbox = self.itemWidget(item)
        if checkbox.isChecked():
            print(f"Tool activated: {checkbox.text()}")
        else:
            print(f"Tool deactivated: {checkbox.text()}")

    def getSelectedTool(self):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.isChecked():
                return widget.text()
        return None

    def setSelectedTool(self, tool_name):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.text() == tool_name:
                widget.setChecked(True)
                self.setCurrentItem(item)  # Optionally highlight the row
                break
