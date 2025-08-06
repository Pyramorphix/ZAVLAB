import sys
from PyQt6.QtWidgets import QApplication
from classApp import ZAVLAB


def main():
    app = QApplication(sys.argv)
    main_window = ZAVLAB()
    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
