import PIL.Image
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Inches
import re

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from widgets.plotTab.plot_widget import plotWidget
from widgets.plotTab.checkbox_widget import ColumnList, ColumnItem
from widgets.plotTab.cursor_widget import CursorDisplay
from widgets.plotTab.reel_widget import Reel, ReelItem

class AddTabDialog(QDialog):
    def __init__(self, parent, columns):
        super(AddTabDialog, self).__init__(parent)
        self.setModal(True)
        self.resize(800, 600)

        self.Layout = QVBoxLayout(self)

        self.name = QLineEdit(self)
        self.name.setPlaceholderText("Enter Category Name")
        self.Layout.addWidget(self.name)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        self.Layout.addWidget(line)

        self.select = QCheckBox("Select All", self)
        self.select.stateChanged.connect(self.selectAll)
        self.Layout.addWidget(self.select)

        self.searchbar = QLineEdit(self)
        self.searchbar.setPlaceholderText("Search Column Name")
        self.searchbar.textChanged.connect(self.updateList)
        self.Layout.addWidget(self.searchbar)

        self.list = QListWidget(self)
        for col in columns:
            item = QListWidgetItem(col, self.list)
            item.setFlags(item.flags()|Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list.addItem(item)
        self.Layout.addWidget(self.list)

        self.box = QDialogButtonBox(self)
        self.box.addButton(QDialogButtonBox.Ok)
        self.box.addButton(QDialogButtonBox.Cancel)

        self.Layout.addWidget(self.box)

        self.box.rejected.connect(self.close)
        self.box.accepted.connect(self.accept)

        self.setLayout(self.Layout)

    def readInput(self):
        text = self.name.text()
        colNames = [self.list.item(i).text() for i in range(self.list.count()) if self.list.item(i).checkState() == Qt.Checked]
        print(colNames)
        return text, colNames
    
    def updateList(self):
        text = self.searchbar.text().lower()

        for i in range(self.list.count()):
            item = self.list.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def selectAll(self):
        select = Qt.Checked if self.select.isChecked() else Qt.Unchecked

        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.isHidden() is False:
                item.setCheckState(select)

class TabBar(QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.df = None
        self.setUsesScrollButtons(True)
        self.setTabsClosable(True)
        self.addTab(PlotTab(self, "Default"), "Default")

        self.tabCloseRequested.connect(self.deleteTab)

    @pyqtSlot(str)
    def read_csv(self, filePath:str):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if filePath.endswith('.csv'):
            self.df = pd.read_csv(filePath)
        elif filePath.endswith('.xlsx'):
            self.df = pd.read_excel(filePath)
        else:
            error = QMessageBox.critical(self, filePath, 'File Format not supported')
            return
        
        QApplication.restoreOverrideCursor()

        columns = list(self.df.columns)
        self.x_col, ok = QInputDialog.getItem(self, 'Select X Column', 'Column', columns)

        if not ok:
            return

        columns = list(self.df.columns.difference([self.x_col]))
        new_cols = [col.split('::')[-1] for col in columns]
        renamed_cols = dict(zip(columns, new_cols))
        self.df.rename(columns=renamed_cols, inplace=True)

        self.columns = list(self.df.columns.difference([self.x_col]))

        for child in self.findChildren(PlotTab):
            child.deleteLater()
        self.clear()

        defaultTab = PlotTab(self, "Default")
        defaultTab.plotWidget.set_df(self.df, self.x_col, self.columns)
        self.addTab(defaultTab, "Default")

        pattern = r'\[([^\[\]]+)\]'
        tab_categories = {match for string in self.columns for match in re.findall(pattern, string)}

        for category in tab_categories:
            tab = PlotTab(self, category)
            cols = [col for col in self.columns if ('['+category+']') in col]
            tab.plotWidget.set_df(self.df, self.x_col, cols)
            self.addTab(tab, category)
    
    def addCategory(self):
        if self.df is None:
            return

        dialog = AddTabDialog(self, self.columns)
        accept = dialog.exec_()
        print(accept)

        if accept:
            name, cols = dialog.readInput()
        else:
            return

        tab = PlotTab(self, name)
        tab.plotWidget.set_df(self.df, self.x_col, cols)
        self.addTab(tab, name)    

    def deleteTab(self, index):
        widget = self.widget(index)
        widget.deleteLater()
        self.removeTab(index)
    
class PlotTab(QWidget):

    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name

        self.setFixedSize(1920, 900)

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(10, 10, 10, 10)

        # Creating checkbox widget
        self.colList = ColumnList(self)
        self.colList.setObjectName("ColumnList")

        # Creating widget to plot graph
        self.plotWidget = plotWidget(self)
        self.plotWidget.setObjectName("plotWidget")

        # Creating Reel
        self.reel = Reel(self)
        self.reel.setObjectName("cursorDisplay")

        # Create Cursor Display Widget
        self.cursorDisplay = CursorDisplay(self)
        self.cursorDisplay.setObjectName("cursorDisplay")

        # Create splitters
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(self.plotWidget)
        vertical_splitter.addWidget(self.reel)
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 3)

        left_splitter = QSplitter(Qt.Horizontal)
        left_splitter.addWidget(self.colList)
        left_splitter.addWidget(vertical_splitter)
        left_splitter.setStretchFactor(0, 2)
        left_splitter.setStretchFactor(1, 1)

        right_splitter = QSplitter(Qt.Horizontal)
        right_splitter.addWidget(left_splitter)
        right_splitter.addWidget(self.cursorDisplay)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)

        self.grid.addWidget(right_splitter, 0, 0)
        self.setLayout(self.grid)

        self.plotWidget.sendColumns.connect(self.colList.read_col_names)
        self.colList.sendUpdateColumnItem.connect(self.UpdateColorBox)
        self.colList.actionSave.triggered.connect(self.savePlotToReel)
        self.colList.sendToggleGrid.connect(self.plotWidget.update_grid)
        self.colList.sendToggleLegend.connect(self.plotWidget.update_legend)
        self.connectCursors()
        
    def UpdateColorBox(self, connect):
        if connect:
            for item in self.colList.findChildren(ColumnItem):
                item.colorChanged.connect(self.plotWidget.update_color)
                item.sendCol.connect(self.plotWidget.plot_column)
        
    def connectCursors(self):
        self.plotWidget.cursor1.sendData.connect(self.cursorDisplay.display1.update_display)
        self.plotWidget.cursor2.sendData.connect(self.cursorDisplay.display2.update_display)
        self.cursorDisplay.display1.sendEnabledSignal.connect(self.plotWidget.cursor1.toggleCursor)
        self.cursorDisplay.display2.sendEnabledSignal.connect(self.plotWidget.cursor2.toggleCursor)
        self.cursorDisplay.display1.sendCurNo.connect(self.plotWidget.setCursor)
        self.cursorDisplay.display2.sendCurNo.connect(self.plotWidget.setCursor)

    def savePlotToReel(self):
        img = np.array(self.plotWidget.canvas.renderer.buffer_rgba())
        comment, ok = QInputDialog.getMultiLineText(self, 'Comment Box', 'Enter Comment :')
        if ok:
            cur_vals = "Delta:\n" + self.cursorDisplay.delta.to_string()
            cur_vals += "Cursor 1:\n" + self.cursorDisplay.display1.to_string()
            cur_vals += "Cursor 2:\n" + self.cursorDisplay.display2.to_string()
            self.reel.add_item(img, comment, cur_vals)
