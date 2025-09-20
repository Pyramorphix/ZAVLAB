import sys
from PyQt6.QtWidgets import QApplication
from main_window import ZAVLABMainWindow



def main():
    app = QApplication(sys.argv)
    main_window = ZAVLABMainWindow()
    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()