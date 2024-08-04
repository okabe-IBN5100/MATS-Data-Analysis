from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backend_bases import MouseButton

from widgets.plotTab.axis_settings import AxisSettingsDialog

from itertools import chain
import datetime

import pandas as pd
import numpy as np

class mplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = None
        super(mplCanvas, self).__init__(self.figure)

class Cursor(QObject):
    sendData = pyqtSignal(dict)

    def __init__(self, parent, canvas:mplCanvas, **kwargs):
        super().__init__(parent)

        self.figure = canvas.figure
        self.canvas = canvas
        self.ax = self.figure.axes[0]

        self.curLine = self.ax.axvline(**kwargs)
        self.enabled = False

    def disable(self):
        self.enabled = False

    def set_cursor(self, df, x_col):
        self.df = df
        self.x_col = x_col
        self.uid = self.canvas.mpl_connect('draw_event', self.update_cursor)

    def on_click(self, event):
        if event.button is MouseButton.RIGHT:
            if self.enabled:
                self.enabled = False
            else:
                self.enabled = True

    def update_cursor(self, event):

        x = self.curLine.get_xdata()[0]

        prev = np.floor(x)
        next = np.ceil(x)

        self.columns = [axis.get_ylabel() for axis in self.figure.axes[1:]]
        next_val = self.df[self.df[self.x_col] == next][self.columns].to_numpy().reshape(-1)
        prev_val = self.df[self.df[self.x_col] == prev][self.columns].to_numpy().reshape(-1)

        curr_val = np.array([np.interp(x ,[prev, next], [prev_val[i], next_val[i]]) for i in range(next_val.size)]).tolist()
        columns = list(self.columns)
        columns.insert(0, self.x_col)
        curr_val.insert(0, prev)

        self.data = dict(zip(columns, curr_val))
        
        self.sendData.emit(self.data)

    def on_hover(self, event):
        if event.inaxes and self.enabled:
            self.curLine.set_xdata(event.xdata)   
            self.canvas.draw()
        
    @pyqtSlot(bool)
    def toggleCursor(self, enable):
        if enable:
            print("cursor enabled")
            self.enabled = True
            self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
            self.hid = self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        else:
            print("cursor disabled")
            self.enabled = False
            self.canvas.mpl_disconnect(self.cid)
            self.canvas.mpl_disconnect(self.hid)

class plotWidget(QWidget):
    sendColumns = pyqtSignal(list)
    sendConnectCursor = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = mplCanvas(self, width=16, height=9, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)

        self.axisAction = self.toolbar.addAction(QIcon(QPixmap(QImage('utils/axis.png'))), 'Y-axis')
        self.axisAction.triggered.connect(self.configureAxis)

        self.canvas.figure.subplots_adjust(right=0.8, left=0.1, bottom=0.1, top=0.95)
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_yticks([])
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)

        self.left_spine = True
        self.curNo = 1

        self.cursor1 = Cursor(self, self.canvas, color='r')
        self.cursor1.curLine.set_label('Cursor 1')

        self.cursor2 = Cursor(self, self.canvas, color='b')
        self.cursor2.curLine.set_label('Cursor 2')

        self.axes = {}

    def configureAxis(self):
        if len(self.axes) == 0:
            error = QMessageBox.warning(self, ' ', 'No Axes Detected')
            return

        dialog = AxisSettingsDialog(self, self.axes)
        dialog.show()
        

    @pyqtSlot(str, bool)
    def plot_column(self, column, isPlot):
        print(column, isPlot)
        color = np.random.rand(3)
        if isPlot:
            self.axes[column] = self.ax.twinx()
            if self.left_spine:
                self.axes[column].yaxis.set_ticks_position('left')
                self.axes[column].yaxis.set_label_position('left')
                self.left_spine = False
            else:
                sep = 0.1 * (len(self.axes) - 2) + 1
                self.axes[column].spines.right.set_position(("axes", sep))
            self.axes[column].plot(self.df[self.x_col], self.df[column], label=column, color=color)
            self.axes[column].set_ylabel(column, loc='bottom')
            self.axes[column].yaxis.label.set_color(color)
            self.axes[column].tick_params(axis='y', colors=color)
        else:
            if column in self.axes:
                self.axes[column].remove()
                self.axes.pop(column)
                self.left_spine = True

                sep = 1
                for col in self.axes:
                    if self.left_spine:
                        self.axes[col].yaxis.set_ticks_position('left')
                        self.axes[col].yaxis.set_label_position('left')
                        self.left_spine = False
                    else:
                        self.axes[col].spines.right.set_position(("axes", sep))
                        sep += 0.1

        self.ax.set_xlabel('Time')

        self.canvas.draw()

    @pyqtSlot(bool)
    def update_grid(self, showGrid):
        if len(self.axes):
            self.axes[list(self.axes.keys())[0]].grid(showGrid)
            self.ax.grid(showGrid)
            self.canvas.draw()

    @pyqtSlot(bool)
    def update_legend(self, showLegend):
        if showLegend:
            lines = []
            legends = []
            for i, column in enumerate(self.axes):
                line, legend = self.axes[column].get_legend_handles_labels()
                lines.append(line); legends.append(legend)

            lines = list(chain(*lines))
            legends = list(chain(*legends))
            self.ax.legend(lines, legends)
        
        else:
            self.ax.get_legend().remove()

        self.canvas.draw()

    def set_df(self, df, x_col, colNames):
        self.df = df
        self.x_col = x_col

        self.ax.set_zorder(1)
        self.ax.patch.set_visible(False)

        self.cursor1.curLine.set_xdata(self.df[x_col][0])
        self.cursor2.curLine.set_xdata(self.df[x_col][0])
        self.cursor1.set_cursor(self.df, x_col)
        self.cursor2.set_cursor(self.df, x_col)

        if colNames:
            self.sendColumns.emit(colNames)

    @pyqtSlot(str, str)
    def update_color(self, column, color):
        print(column, color) #debugging purposes
        if column in self.axes:
            self.axes[column].get_lines()[0].set_color(color)
            self.axes[column].yaxis.label.set_color(color)
            self.axes[column].tick_params(axis='y', colors=color)

            legend = self.ax.get_legend()
            legend_texts = [text.get_text() for text in legend.get_texts()]
            legend_lines = legend.get_lines()

            ind = legend_texts.index(column)
            legend_lines[ind].set_color(color)

        self.canvas.draw()

    def setCursor(self, curNo):
        self.curNo = curNo




