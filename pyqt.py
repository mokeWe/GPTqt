import sys
import openai
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QSlider,
    QTextEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QMessageBox,
)
from pathlib import Path
import qdarktheme


class MainWin(QWidget):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)

        # adding widgets
        self.tempAmount = float(0.1)
        self.answerAmount = 1
        self.tokenAmount = 10

        self.tempSlide = QSlider(Qt.Orientation.Horizontal)
        self.tokenSlide = QSlider(Qt.Orientation.Horizontal)
        self.amountSlide = QSlider(Qt.Orientation.Horizontal)

        self.promptEdit = QTextEdit()
        self.responseBox = QTextEdit()

        self.tokenStatus = QLabel("Tokens: 10")
        self.tempStatus = QLabel("Temp: 0.0")
        self.amountStatus = QLabel("Answers: 1")
        self.engineStatus = QLabel("Engine: ")
        self.finished = QLabel()

        self.sendButton = QPushButton("Send prompt")
        self.engine = QComboBox()

        # connections
        self.engine.currentIndexChanged.connect(self.value_change)

        self.tokenSlide.setRange(10, 1000)
        self.tokenSlide.valueChanged.connect(self.value_change)

        self.amountSlide.setRange(1, 5)
        self.amountSlide.valueChanged.connect(self.value_change)

        self.tempSlide.setRange(0, 10)
        self.tempSlide.valueChanged.connect(self.value_change)

        self.responseBox.setReadOnly(True)

        self.sendButton.clicked.connect(self.send_prompt)

    def init_ui(self):
        _keypath = Path("api-key.txt")
        _keypath.touch(exist_ok=True)

        with open("api-key.txt", "r") as h:
            _key = h.readline().strip("\n")
        if not _key.startswith("sk-"):
            QMessageBox.critical(
                self,
                "Error",
                "API Key not found, or an invalid API key was provided. Set a "
                "valid key in api-key.txt!",
            )
            sys.exit()

        openai.api_key = _key

        models = openai.Model.list()

        # exclude useless models
        exclude = [
            "instruct",
            "similarity",
            "if",
            "query",
            "document",
            "insert",
            ":",
            "search",
            "edit",
        ]

        self.engine.addItems(
            list(
                filter(
                    lambda x: not any(y in x for y in exclude),
                    map(lambda x: str(x.id), models.data),
                )
            )
        )

        self.cEngine = self.engine.currentText()

        l = QGridLayout()
        l.aw = lambda w, r, c: l.addWidget(w, r, c)
        l.aw(self.tempStatus, 0, 0)
        l.aw(self.tempSlide, 0, 1)
        l.aw(self.tokenStatus, 1, 0)
        l.aw(self.tokenSlide, 1, 1)
        l.aw(self.amountStatus, 2, 0)
        l.aw(self.amountSlide, 2, 1)
        l.aw(self.engineStatus, 3, 0)
        l.aw(self.engine, 3, 1)
        l.addWidget(self.promptEdit, 4, 0, 1, 2)
        l.addWidget(self.sendButton, 5, 0, 1, 2)
        l.addWidget(self.responseBox, 6, 0, 1, 2)
        l.addWidget(self.finished, 7, 0, 1, 2)
        self.setLayout(l)

    def selection_change(self):
        self.cEngine = self.engine.currentText()

    def value_change(self):
        self.tokenAmount = self.tokenSlide.value()
        self.tempAmount = self.tempSlide.value() / 10
        self.answerAmount = self.amountSlide.value()
        self.tokenStatus.setText("Tokens: " + str(self.tokenAmount))
        self.tempStatus.setText("Temp: " + str(self.tempAmount))
        self.amountStatus.setText("Answers: " + str(self.answerAmount))

    def send_prompt(self):
        response = openai.Completion.create(
            engine=self.cEngine,
            prompt=self.promptEdit.toPlainText(),
            temperature=float(self.tempAmount),
            max_tokens=int(self.tokenAmount),
            top_p=0.5,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            n=int(self.answerAmount),
        )

        # set text box as response
        self.responseBox.setText("")

        for i in range(int(self.answerAmount)):
            self.responseBox.append("[+] ANSWER " + str(i + 1))
            self.responseBox.append(response.choices[i].text + "\n\n\n")

        # write response text to file
        f = open("Responses.txt", "a+")

        f.write(f"Prompt: {self.promptEdit.toPlainText()} | Engine: {self.cEngine}\n")

        for i in range(int(self.answerAmount)):
            f.write(f"\n[+]----------ANSWER-{i + 1}---------\n")
            f.write(response.choices[i].text + "\n")
            f.write("[+]--------------------------\n\n")

        f.close()
        self.finished.setText("[+] Done! Also saved to Responses.txt")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    ex = MainWin()
    ex.init_ui()
    ex.setWindowIcon(QIcon("icon.png"))
    ex.resize(500, 600)
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
