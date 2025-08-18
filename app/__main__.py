from .ss_ui import MainWindow
from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
