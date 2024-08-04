from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DeltaDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.addStretch()
        self.layout.setDirection(QBoxLayout.BottomToTop)

        self.seperator = QFrame(self)
        self.seperator.setFrameShape(QFrame.HLine|QFrame.Sunken)
        self.layout.addWidget(self.seperator)

        self.display = QTableWidget(self)
        self.display.setColumnCount(2)
        self.display.setHorizontalHeaderItem(0, QTableWidgetItem("Column"))
        self.display.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        self.display.horizontalHeader().setStretchLastSection(True) 
        self.display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.display.verticalHeader().setVisible(False)
        self.layout.addWidget(self.display)

        self.heading = QLabel("Delta")
        self.heading.setTextFormat(Qt.RichText)
        self.heading.setMargin(15)
        self.layout.addWidget(self.heading)

        self.display_text = ""
        self.data1 = None
        self.data2 = None
        self.delta = None

        self.setLayout(self.layout)

    @pyqtSlot(dict, int)
    def update_display(self, data, curNo):
        if curNo == 1:
            self.data1 = data
        else :
            self.data2 = data

        self.display_text = f""
        
        if self.data1 and self.data2:
            if len(self.data1) == len(self.data2):
                self.display.clearContents()

                self.display.setRowCount(len(self.data1))
                for row, column in enumerate(self.data1):
                    val = str(abs(round((self.data1[column] - self.data2[column]), 3)))
                    item = QTableWidgetItem(column);item.setToolTip(column)
                    self.display.setItem(row, 0, item)
                    item = QTableWidgetItem(val);item.setToolTip(val)
                    self.display.setItem(row, 1, item)

    def to_string(self):
        text = ""
        for row in range(self.display.rowCount()):
            column = self.display.item(row, 0).text()
            val = self.display.item(row, 1).text()
            text += f"{column} : {val}\n"
            
        return text


class CursorDisplayItem(QWidget):
    sendEnabledSignal = pyqtSignal(bool)
    sendCurNo = pyqtSignal(int)

    sendToDelta = pyqtSignal(dict, int)

    def __init__(self, parent=None, no=1):
        super().__init__(parent)
        self.curNo = no

        self.layout = QVBoxLayout(self)
        self.layout.addStretch()
        self.layout.setDirection(QBoxLayout.BottomToTop)

        self.seperator = QFrame(self)
        self.seperator.setFrameShape(QFrame.HLine|QFrame.Sunken)
        self.layout.addWidget(self.seperator)

        self.display = QTableWidget(self)
        self.display.setColumnCount(2)
        self.display.setHorizontalHeaderItem(0, QTableWidgetItem("Column"))
        self.display.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        self.display.horizontalHeader().setStretchLastSection(True) 
        self.display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.display.verticalHeader().setVisible(False)
        self.layout.addWidget(self.display)

        self.radio_button = QRadioButton(self)
        self.radio_button.setText(f'Cursor {self.curNo}')
        self.radio_button.toggled.connect(self.send_toggle_signal)
        self.radio_button.setToolTip(f"Toggle Cursor {no}\nRight Click to lock Cursor")
        self.layout.addWidget(self.radio_button)

        self.setLayout(self.layout)

    def to_string(self):
        text = ""
        for row in range(self.display.rowCount()):
            column = self.display.item(row, 0).text()
            val = self.display.item(row, 1).text()
            text += f"{column} : {val}\n"

        return text

    @pyqtSlot(dict)
    def update_display(self, data):
        self.data = data
        self.sendToDelta.emit(data, self.curNo)

        self.display.clearContents()

        self.display.setRowCount(len(data))
        for row, column in enumerate(data):
            val = str(round((data[column]), 3))
            item = QTableWidgetItem(column);item.setToolTip(column)
            self.display.setItem(row, 0, item)
            item = QTableWidgetItem(val);item.setToolTip(val)
            self.display.setItem(row, 1, item)

    def send_toggle_signal(self):
        if self.radio_button.isChecked():
            enable = True
            self.sendEnabledSignal.emit(enable)
            curNo = self.curNo
            self.sendCurNo.emit(curNo)
        else:
            enable = False
            self.sendEnabledSignal.emit(enable)

class CursorDisplay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_content = QWidget(self.scroll_area)

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.addStretch()
        self.scroll_layout.setDirection(QBoxLayout.BottomToTop)
        
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

        self.radioGroup = QButtonGroup(self)

        self.display1 = CursorDisplayItem(self, 1)
        self.radioGroup.addButton(self.display1.radio_button)
        self.scroll_layout.addWidget(self.display1)

        self.display2 = CursorDisplayItem(self, 2)
        self.radioGroup.addButton(self.display2.radio_button)
        self.scroll_layout.addWidget(self.display2)

        self.delta = DeltaDisplay(self)
        self.scroll_layout.addWidget(self.delta)

        self.display1.sendToDelta.connect(self.delta.update_display)
        self.display2.sendToDelta.connect(self.delta.update_display)

        self.setLayout(self.layout)
