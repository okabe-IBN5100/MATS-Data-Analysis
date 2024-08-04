from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np

class ReelItem(QWidget):
    def __init__(self, parent=None, img=None, annotation=None, cursor_vals=None):
        super().__init__(parent)

        self.img = img
        self.annotation = annotation
        self.cursor_vals = cursor_vals

        self.layout = QHBoxLayout(self)

        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(True)
        self.layout.addWidget(self.checkbox)

        self.img_display = QLabel(self)
        self.img_display.setPixmap(QPixmap.fromImage(self.rgb2qimage(self.img).scaled(180, 180)))
        self.layout.addWidget(self.img_display)

        self.seperator = QFrame(self)
        self.seperator.setFrameShape(QFrame.VLine|QFrame.Sunken)
        self.layout.addWidget(self.seperator)

        self.menu = QMenu(self)

        self.showAction = QAction(self.menu)
        self.showAction.triggered.connect(self.show)
        self.showAction.setText("Show")
        self.menu.addAction(self.showAction)

        self.deleteAction = QAction(self.menu)
        self.deleteAction.triggered.connect(self.delete)
        self.deleteAction.setText("Delete")
        self.menu.addAction(self.deleteAction)

        self.mouseReleaseEvent = self.show_menu
        self.setToolTip("Right Click for Options")

    def rgb2qimage(self, img:np.array)->QImage:
        if img is not None:
            h, w = self.img.shape[:2]
    
            bgra = np.empty((h, w, 4), np.uint8, 'C')
            bgra[...,0] = img[...,2]
            bgra[...,1] = img[...,1]
            bgra[...,2] = img[...,0]
            bgra[...,3] = img[...,3]
            qt_image = QImage(bgra.data, w, h, QImage.Format_RGB32)

            return qt_image
        
    def delete(self):
        self.deleteLater()
        
    def show_menu(self, event:QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:

            self.menu.popup(event.globalPos())

    def show(self):
        message_box = QDialog()
        message_box.resize(1280, 720)
        layout = QVBoxLayout(message_box)

        img = QLabel(message_box)
        img.setPixmap(QPixmap.fromImage(self.rgb2qimage(self.img)))
        layout.addWidget(img)

        annotation = QLabel(message_box)
        annotation.setText(f"Cursor Values :\n{self.cursor_vals}\n Comment:\n{self.annotation}")
        layout.addWidget(annotation)

        message_box.setLayout(layout)
        message_box.exec_()
        
class Reel(QWidget):
    sendSelectedColumns = pyqtSignal(list)
    sendUpdateColumnItem = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QHBoxLayout(self)
        
        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_layout = QHBoxLayout(self.scroll_content)

        self.scroll_layout.addStretch()
        self.scroll_layout.setDirection(QBoxLayout.RightToLeft)
        
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def add_item(self, img, comment, cursor_vals):
        item = ReelItem(self, img, comment, cursor_vals)
        item.setObjectName("ReelItem")
        self.scroll_layout.addWidget(item)


    