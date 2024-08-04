import sys
import multiprocessing
from app import *

def run():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    run()