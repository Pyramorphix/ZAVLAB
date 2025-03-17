import sys
from PyQt5.QtWidgets import QApplication
from ZAVLAB.app import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
