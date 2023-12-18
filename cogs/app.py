from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout,
)
import qdarktheme
import time
from cogs.tabs import Tab1, Tab2, Tab3
from cogs.apis import *


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "GPTQT"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 600, 600)

        # make tabbed window
        self.tabs = QTabWidget()

        self.tab1 = Tab1()
        self.tab1.init_ui()
        self.tabs.addTab(self.tab1, "Requests")

        self.tab2 = Tab2()
        self.tab2.init_ui()
        self.tabs.addTab(self.tab2, "Chat")

        self.tab3 = Tab3()
        self.tab3.init_ui()
        self.tabs.addTab(self.tab3, "Chat Settings")

        # set layout
        l = QVBoxLayout()
        l.addWidget(self.tabs)
        self.setLayout(l)

        self.setStyleSheet(qdarktheme.load_stylesheet())

        self.show()
