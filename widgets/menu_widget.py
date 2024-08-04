from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MenuWidget(QWidget):
    fileSelected = pyqtSignal(str)
    sendGridOn = pyqtSignal(bool)
    newWindow = pyqtSignal(bool)
    sendExport = pyqtSignal(bool)
    sendCategory = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menubar = QMenuBar(parent)
        self.menubar.setGeometry(QRect(0, 0, 800, 27))
        self.menubar.setObjectName("menubar")

        #File tab
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        #File new window option
        self.createNewWindow = QAction(parent)
        self.menuFile.addAction(self.createNewWindow)
        self.createNewWindow.setObjectName("createNewWindow")
        
        #File open option
        self.actionOpen = QAction(parent)
        self.menuFile.addAction(self.actionOpen)
        self.actionOpen.setObjectName("actionOpen")

        #File Export Reel Tab
        self.exportReel = QAction(parent)
        self.menuFile.addAction(self.exportReel)
        self.exportReel.setObjectName("actionExport")

        #File Add Category
        self.actionAddCategory = QAction(parent)
        self.menuFile.addAction(self.actionAddCategory)
        self.actionAddCategory.setObjectName("actionAddCategory")

        #About tab
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")

        parent.setMenuBar(self.menubar)

        self.actionOpen.triggered.connect(self.openFileDialog)
        self.createNewWindow.triggered.connect(self.send_new_window)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.createNewWindow.setText("New")
        self.menuFile.setTitle("File")
        self.menuAbout.setTitle("About")
        self.actionOpen.setText("Open")
        self.exportReel.setText("Export Reel")
        self.actionAddCategory.setText("Add Category")

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filePath, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", "All (*);; CSV Files (*.csv);; Excel File (*.xlsx)", options=options)
        if filePath:
            print(f"Selected file: {filePath}")
            self.fileSelected.emit(filePath)

    def send_new_window(self, send=True):
        self.newWindow.emit(send)



    

    