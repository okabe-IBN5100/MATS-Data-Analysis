from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import time

class ListItem(QListWidgetItem):
    def __init__(self, parent, colName):
        super(ListItem, self).__init__(parent)

        self.colName = colName

class ColumnItem(QWidget):
    colorChanged = pyqtSignal(str, str)
    sendCol = pyqtSignal(str, bool)

    def __init__(self, colName, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        
        self.checkbox = QCheckBox(self)
        self.checkbox.stateChanged.connect(self.send_column)

        color_icon = QIcon(QPixmap(QImage('utils/color-picker.png')))
        self.color_button = QPushButton(color_icon, "", self)
        self.color_button.setStyleSheet("background-color: white; margin: 1px;")
        self.color_button.clicked.connect(self.pick_color)

        self.label = QLabel(colName, self)
        self.label.setToolTip(colName)

        self.layout.addWidget(self.checkbox, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.color_button, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.label, alignment=Qt.AlignRight)

        self.layout.addStretch()
        self.layout.setDirection(QBoxLayout.LeftToRight)
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)

    def pick_color(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            column = self.label.text()
            color = self.color
            self.colorChanged.emit(column, color)

    def send_column(self):
        column = self.label.text()
        isPlot = self.checkbox.isChecked()
        self.sendCol.emit(column, isPlot)

class ColumnList(QWidget):
    sendUpdateColumnItem = pyqtSignal(bool)
    sendToggleGrid = pyqtSignal(bool)
    sendToggleLegend = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.colNames = []
        self.layout = QVBoxLayout(self)

        self.ButtonBox = QHBoxLayout()
        self.ButtonBox.setDirection(QBoxLayout.LeftToRight)

        self.resetButton = QPushButton(QIcon.fromTheme('view-refresh'), "Reset")
        self.resetButton.setMaximumWidth(100)
        self.resetButton.pressed.connect(self.resetCols)
        self.ButtonBox.addWidget(self.resetButton)

        self.options = QMenu(self)

        self.actionSave = QAction('Save To Reel', self.options)
        self.options.addAction(self.actionSave)

        self.actionToggleGrid = QAction('Toggle Grid', self.options, checkable=True)
        self.options.addAction(self.actionToggleGrid)
        self.actionToggleGrid.triggered.connect(self.toggleGrid)

        self.actionToggleLegend = QAction('Toggle Legend', self.options, checkable=True)
        self.options.addAction(self.actionToggleLegend)
        self.actionToggleLegend.triggered.connect(self.toggleLegend)

        self.optionsButton = QPushButton('Tools')
        self.optionsButton.setMaximumWidth(100)
        self.optionsButton.setMenu(self.options)
        self.ButtonBox.addWidget(self.optionsButton)

        self.ButtonBox.addStretch(0)
        self.layout.addLayout(self.ButtonBox)

        self.searchbar = QLineEdit(self)
        self.searchbar.setPlaceholderText("Search...")
        self.searchbar.textChanged.connect(self.updateList)
        self.layout.addWidget(self.searchbar)
        
        self.list = QListWidget(self)
        self.list.itemActivated.connect(self.on_click)
        self.layout.addWidget(self.list)


    @pyqtSlot(list)
    def read_col_names(self, colNames):
        self.colNames = colNames

        self.list.clear()
        for widget in self.findChildren(ColumnList):
            widget.deleteLater()

        for colName in self.colNames:
            widget = ColumnItem(colName, self.list)
            widget.setObjectName(colName)
            
            item = ListItem(self.list, colName)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

        connect = True
        self.sendUpdateColumnItem.emit(connect)

    def on_click(self, item):
        widget = self.list.itemWidget(item)

        if widget.checkbox.isChecked():
            widget.checkbox.setChecked(False)
        else:
            widget.checkbox.setChecked(True)

    def updateList(self):
        text = self.searchbar.text().lower()

        for i in range(self.list.count()):
            item = self.list.item(i)
            if text in item.colName.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def resetCols(self):
        for i in range(self.list.count()):
            widget = self.list.itemWidget(self.list.item(i))
            widget.checkbox.setCheckState(Qt.Unchecked)

    def toggleGrid(self):
        showGrid = self.actionToggleGrid.isChecked()
        self.sendToggleGrid.emit(showGrid)

    def toggleLegend(self):
        showLegend = self.actionToggleLegend.isChecked()
        self.sendToggleLegend.emit(showLegend)
    


        