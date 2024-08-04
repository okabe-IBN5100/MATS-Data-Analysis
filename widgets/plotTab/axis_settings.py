from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import matplotlib
import matplotlib.axes

class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class VerticalTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar())
        self.setTabPosition(QTabWidget.West)

class SettingsTab(QWidget):
    def __init__(self, parent, axis:matplotlib.axes.Axes):
        super(SettingsTab, self).__init__(parent)
        self.setMinimumSize(300, 500)

        self.axis = axis

        self.Layout = QVBoxLayout(self)
        self.form = QFormLayout()

        left, right = self.axis.get_ylim()

        self.min = QLineEdit(self)
        self.min.setValidator(QDoubleValidator(self.min))
        self.min.setText(str(left))
        self.form.addRow('Min :', self.min)

        self.max = QLineEdit(self)
        self.min.setValidator(QDoubleValidator(self.min))
        self.max.setText(str(right))
        self.form.addRow('Max :', self.max)

        self.scaleOptions = QComboBox(self)
        self.scaleOptions.addItems(['linear', 'log'])
        self.scaleOptions.setCurrentIndex(0)
        self.form.addRow('Scale :', self.scaleOptions)

        self.Layout.addLayout(self.form)

        self.apply = QDialogButtonBox(self)
        self.apply.addButton(QDialogButtonBox.Apply)
        self.Layout.addWidget(self.apply)

    def setOptions(self):
        if len(self.min.text()) > 0 and len(self.max.text()) > 0:
            self.axis.set_ylim(bottom=float(self.min.text()), top=float(self.max.text()))

        self.axis.set_yscale(self.scaleOptions.currentText())

        self.axis.figure.canvas.draw()



class AxisSettingsDialog(QDialog):
    def __init__(self, parent, axes):
        super(AxisSettingsDialog, self).__init__(parent)
        self.setModal(False)

        self.Layout = QHBoxLayout(self)
        
        self.axes = axes
        self.columns = [column for column in self.axes]

        self.tabs = VerticalTabWidget()

        for column in self.columns:
            self.tabs.addTab(SettingsTab(self, self.axes[column]), column)

        self.Layout.addWidget(self.tabs)

