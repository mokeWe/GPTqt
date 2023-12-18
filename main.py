import sys
from PyQt6.QtWidgets import QApplication
from cogs.app import App


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
