import sys
import openai
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QSlider, QTextEdit, QPushButton, QComboBox, QVBoxLayout, \
    QMessageBox
from pathlib import Path
import qdarktheme


class MainWin(QWidget):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.tempAmount = float(0.1)
        self.answerAmount = 1
        self.tokenAmount = 10
        self.cEngine = 'davinci'
        self.tempSlide = QSlider(Qt.Orientation.Horizontal)
        self.tokenSlide = QSlider(Qt.Orientation.Horizontal)
        self.amountSlide = QSlider(Qt.Orientation.Horizontal)
        self.tokenStatus = QLabel("Answers: 1")
        self.promptEdit = QTextEdit()
        self.responseBox = QTextEdit()
        self.tokenStatus = QLabel("Tokens: 10")
        self.sendButton = QPushButton("Send prompt")
        self.tempStatus = QLabel("Temperature: 0.0")
        self.amountStatus = QLabel("Answers: 1")
        self.engine = QComboBox()
        self.finished = QLabel()

    def init_ui(self):
        _keypath = Path('api-key.txt')
        _keypath.touch(exist_ok=True)
        with open('api-key.txt', 'r') as h:
            _key = h.readline()
        if _key.startswith('sk-'):
            openai.api_key = _key
        else:
            QMessageBox.critical(self, "Hey!", 'API Key not found, or an invalid API key was provided. Set a '
                                               'valid key in api-key.txt!')
            sys.exit()

        self.engine.addItems(['davinci', 'curie', 'babbage', 'ada'])
        self.engine.currentIndexChanged.connect(self.selection_change)
        # token slider
        self.tokenSlide.setMinimum(10)
        self.tokenSlide.setMaximum(2000)
        self.tokenSlide.valueChanged.connect(self.token_value)
        # amount slider
        self.amountSlide.setMinimum(1)
        self.amountSlide.setMaximum(5)
        self.amountSlide.valueChanged.connect(self.amount_value)
        # temperature slider
        self.tempSlide.setMinimum(0)
        self.tempSlide.setMaximum(15)
        self.tempSlide.valueChanged.connect(self.change_value_temp)
        # text editor for prompt
        self.responseBox.setReadOnly(True)
        # prompt sender
        self.sendButton.setToolTip("Submit the prompt")  # Tool tip
        self.sendButton.clicked.connect(self.send_prompt)
        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.engine)
        layout.addWidget(self.amountStatus)
        layout.addWidget(self.amountSlide)
        layout.addWidget(self.tokenStatus)
        layout.addWidget(self.tokenSlide)
        layout.addWidget(self.tempStatus)
        layout.addWidget(self.tempSlide)
        layout.addWidget(self.promptEdit)
        layout.addWidget(self.sendButton)
        layout.addWidget(self.responseBox)
        layout.addWidget(self.finished)
        self.setLayout(layout)

    def selection_change(self):
        self.cEngine = self.engine.currentText()

    def token_value(self):
        self.tokenAmount = self.tokenSlide.value()
        self.tokenStatus.setText("Tokens: " + str(self.tokenSlide.value()))

    def change_value_temp(self):
        self.tempAmount = self.tempSlide.value() / 10
        self.tempStatus.setText("Temperature: " + str(self.tempSlide.value() / 10))

    def amount_value(self):
        self.answerAmount = self.amountSlide.value()
        self.amountStatus.setText("Answers: " + str(self.amountSlide.value()))

    def send_prompt(self):
        response = openai.Completion.create(
            engine="text-" + self.cEngine + "-001",
            prompt=self.promptEdit.toPlainText(),
            temperature=float(self.tempAmount),
            max_tokens=int(self.tokenAmount),
            top_p=0.5,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            n=int(self.answerAmount)
        )
        # set text box as response
        self.responseBox.setText("")
        if int(self.answerAmount) > 0:
            for i in range(int(self.answerAmount)):
                self.responseBox.append("[+]----------ANSWER-" + str(i + 1) + "---------")
                self.responseBox.append(response.choices[i].text + "\n\n\n")

        # write response text to file
        f = open("Responses.txt", "a+")
        if int(self.answerAmount) > 0:
            f.write("Prompt: " + self.promptEdit.toPlainText() + " | Engine: " + self.cEngine + "\n")
            for i in range(int(self.answerAmount)):
                f.write("\n[+]----------ANSWER-" + str(i + 1) + "---------\n")
                f.write(response.choices[i].text + "\n")
                f.write("[+]--------------------------\n\n")
        f.close()
        self.finished.setText('[+] Done! Also saved to Responses.txt')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    ex = MainWin()
    ex.init_ui()
    ex.setWindowIcon(QIcon('icon.png'))
    ex.resize(500, 600)
    ex.show()
    sys.exit(app.exec())
