import sys
from main_window import ZAVLABMainWindow
import traceback
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox

def global_exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception hook that triggers autosave on any unhandled error."""
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error(f"[CRITICAL] Unhandled exception:\n{error_text}")

    try:
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if hasattr(widget, "auto_save_on_crash"):
                    widget.auto_save_on_crash()
    except Exception as save_err:
        logging.error(f"[CRITICAL] Autosave failed: {save_err}")

    try:
        msg = QMessageBox()
        msg.setWindowTitle("Critical Error")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("A critical error has occurred.\nThe data was automatically saved.")
        msg.setDetailedText(error_text)
        msg.exec()
    except Exception:
        pass
    sys.exit(1)


def main():
    sys.excepthook = global_exception_hook

    app = QApplication(sys.argv)
    main_window = ZAVLABMainWindow()
    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()