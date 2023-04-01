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
    QTabWidget,
    QLineEdit,
    QVBoxLayout,
)
from pathlib import Path
import qdarktheme


messages = []


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "GPTQT"
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
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


# Response tab
class Tab1(QWidget):
    def __init__(self, parent=None):
        """Initialize tab1"""
        super(Tab1, self).__init__(parent)

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
        """Initialize the UI for tab1"""
        global _key
        global models
        global exclude

        _keypath = Path("api-key.txt")
        _keypath.touch(exist_ok=True)

        print("Loading API key...")

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

        # Add items to the combobox
        print("Loading engines...")
        self.engine.addItems(
            # Filter out items that are not needed
            list(
                filter(
                    # Filter out items that should be excluded
                    lambda x: not any(y in x for y in exclude),
                    # Get the item's id
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
        """Update the engine when the combobox is changed"""
        self.cEngine = self.engine.currentText()

    def value_change(self):
        """Update the values when the sliders are changed"""
        self.tokenAmount = self.tokenSlide.value()
        self.tempAmount = self.tempSlide.value() / 10
        self.answerAmount = self.amountSlide.value()
        self.tokenStatus.setText("Tokens: " + str(self.tokenAmount))
        self.tempStatus.setText("Temp: " + str(self.tempAmount))
        self.amountStatus.setText("Answers: " + str(self.answerAmount))

    def send_prompt(self):
        """Send the prompt to OpenAI"""

        print("Sending prompt...")

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

        # Set the text box as response
        self.responseBox.setText("")

        for i in range(int(self.answerAmount)):
            self.responseBox.append("[+] ANSWER " + str(i + 1))
            self.responseBox.append(response.choices[i].text + "\n\n\n")

        # Write response text to file
        f = open("Responses.txt", "a+")

        f.write(f"Prompt: {self.promptEdit.toPlainText()} | Engine: {self.cEngine}\n")

        for i in range(int(self.answerAmount)):
            f.write(f"\n[+]----------ANSWER-{i + 1}---------\n")
            f.write(response.choices[i].text + "\n")
            f.write("[+]--------------------------\n\n")

        f.close()
        self.finished.setText("[+] Done! Also saved to Responses.txt")


# Chat tab
class Tab2(QWidget):
    def __init__(self, parent=None):
        super(Tab2, self).__init__(parent)

        # adding widgets
        self.responseLabel = QLabel("Response:")
        self.responseBox = QTextEdit()
        self.responseBox.setReadOnly(True)

        self.promptEdit = QLineEdit()
        self.promptEdit.setFixedHeight(100)

    def init_ui(self):
        """Initialize the UI for tab2"""
        l = QGridLayout()
        l.addWidget(self.responseLabel, 0, 0)
        l.addWidget(self.responseBox, 1, 0)
        l.addWidget(self.promptEdit, 2, 0)
        self.setLayout(l)

        # read responses from file
        # f = open("chat_log.txt", "r")
        # self.responseBox.setText(f.read())
        # f.close()

        # set ghost text for prompt
        self.promptEdit.setPlaceholderText("Enter your prompt here...")
        self.promptEdit.returnPressed.connect(self.generate_response)

    def generate_response(self):
        """Generate a response from the prompt"""
        global msg_content
        global messages

        prompt = self.promptEdit.text()
        self.promptEdit.setText("")
        self.responseBox.append(f"\nUser: {prompt}\n")

        print(f"User: {prompt}")

        messages.append({"role": "user", "content": f"{prompt}"})

        response = openai.ChatCompletion.create(
            model=chat_engine,
            temperature=tempAmount,
            max_tokens=tokenAmount,
            messages=messages,
        )

        messages.append(
            {"role": "assistant", "content": f"{response.choices[0].message.content}"}
        )

        print(messages)

        print(f"Bot: {response.choices[0].message.content}")

        self.responseBox.append(f"Bot: {response.choices[0].message.content}")


# Chat Settings Tab
class Tab3(QWidget):
    def __init__(self, parent=None):
        super(Tab3, self).__init__(parent)

        # adding widgets
        self.tempAmount = float(0.1)
        self.tokenAmount = 10

        self.tempSlide = QSlider(Qt.Orientation.Horizontal)
        self.tokenSlide = QSlider(Qt.Orientation.Horizontal)

        self.tokenStatus = QLabel("Tokens: 10")
        self.tempStatus = QLabel("Temp: 0.0")
        self.engineStatus = QLabel("Engine: ")

        self.tokenSlide.setRange(10, 1000)
        self.tokenSlide.valueChanged.connect(self.selection_change)

        self.tempSlide.setRange(0, 10)
        self.tempSlide.valueChanged.connect(self.selection_change)

        self.engineBox = QComboBox()

        # Kinda broken, allows user to select completion models.
        self.engineBox.addItems(
            # Filter out items that are not needed
            list(
                filter(
                    lambda x: not any(y in x for y in exclude),
                    map(lambda x: str(x.id), models.data),
                )
            )
        )

        self.engineBox.currentIndexChanged.connect(self.selection_change)

    def selection_change(self):
        """Update the values when the sliders are changed"""
        global tokenAmount
        self.tokenAmount = self.tokenSlide.value()
        tokenAmount = self.tokenAmount
        self.tokenStatus.setText(f"Tokens: {self.tokenAmount}")

        global tempAmount
        self.tempAmount = self.tempSlide.value() / 10
        tempAmount = self.tempAmount
        self.tempStatus.setText(f"Temp: {self.tempAmount}")

        global chat_engine
        chat_engine = self.engineBox.currentText()

    def init_ui(self):
        """Initialize the UI for tab3"""
        layout = QGridLayout()
        layout.setRowStretch(10, 1)
        law = lambda w, r, c: layout.addWidget(w, r, c)
        law(self.engineBox, 0, 0)
        law(self.tempStatus, 1, 0)
        law(self.tempSlide, 2, 0)
        law(self.tokenStatus, 3, 0)
        law(self.tokenSlide, 4, 0)

        self.setLayout(layout)


def main():
    """Main function"""
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
