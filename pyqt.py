import sys
import openai
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
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
    QTabWidget,
    QLineEdit,
    QVBoxLayout,
)
from pathlib import Path
import qdarktheme
import time


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

    # function to load API key from file
    def load_api_key():
        global _key

        _keypath = Path("api-key.txt")
        _keypath.touch(exist_ok=True)

        print("     Loading API key...")

        with open("api-key.txt", "r") as h:
            _key = h.readline().strip("\n")
        if not _key:
            print(
                "No API key found, or an invalid one was detected. Set a valid key in api-key.txt"
            )
            sys.exit()
        else:
            print("     API key loaded successfully!")

        openai.api_key = _key

    def load_models():
        global model_list

        models = openai.Model.list()

        # exclude useless models
        exclude = [
            "instruct",
            "similarity",
            "if",
            "query",
            "document",
            "insert",
            "search",
            "edit",
            "dall-e",
            "tts"
        ]

        print("     loading engines...")

        model_list = []

        model_list = [
            str(model.id)
            for model in models.data
            if not any(y in str(model.id) for y in exclude)
        ]

        print("     engines loaded successfully")

    # loading API key and models in the background
    time_start = time.time()
    load_api_key()
    load_models()
    time_end = time.time() - time_start
    print(f"Loaded in {time_end} seconds")


class Tab1(QWidget):
    def __init__(self, parent=None):
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
        self.engine.addItems(model_list)

        # connections
        self.engine.currentIndexChanged.connect(self.value_change)

        self.tokenSlide.setRange(10, 1000)
        self.tokenSlide.valueChanged.connect(self.value_change)

        self.amountSlide.setRange(1, 5)
        self.amountSlide.valueChanged.connect(self.value_change)

        self.tempSlide.setRange(0, 10)
        self.tempSlide.valueChanged.connect(self.value_change)

        self.responseBox.setReadOnly(True)

        self.sendButton.clicked.connect(self.send_prompt_thread)

    def init_ui(self):
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

    def send_prompt_thread(self):
        self.sendButton.setEnabled(False)
        self.finished.setText("Sending prompt...")
        self.finished.repaint()
        self.send_prompt()
        self.sendButton.setEnabled(True)

    def send_prompt(self):
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

        print("Done!")


messages = []


# Chat tab
class Tab2(QWidget):
    def __init__(self, parent=None):
        super(Tab2, self).__init__(parent)

        # adding widgets
        self.responseLabel = QLabel("Response:")
        self.responseBox = QTextEdit()
        self.responseBox.setReadOnly(True)
        self.promptEdit = QLineEdit()

    def init_ui(self):
        l = QGridLayout()
        l.addWidget(self.responseLabel, 0, 0)
        l.addWidget(self.responseBox, 1, 0)
        l.addWidget(self.promptEdit, 2, 0)
        self.setLayout(l)

        # set ghost text for prompt
        self.promptEdit.setPlaceholderText("Enter your prompt here...")
        self.promptEdit.returnPressed.connect(self.generate_response)

    def generate_response(self):
        # set up threading to stop the UI from freezing

        global messages

        prompt = self.promptEdit.text()
        self.promptEdit.setText("")
        self.responseBox.append(f"\nUser: {prompt}\n\nBot: ")

        messages.append({"role": "user", "content": f"{prompt}"})

        self.thread = QThread()
        self.worker = Worker(responseBox=self.responseBox)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.worker.progress.connect(self.update_text_box)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

    def update_text_box(self, text_chunk):
        self.responseBox.insertPlainText(text_chunk)


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, responseBox):
        super().__init__()
        self.responseBox = responseBox

    def generate_response(self):
        global messages

        response = openai.ChatCompletion.create(
            model=chat_engine,
            temperature=tempAmount,
            max_tokens=tokenAmount,
            messages=messages,
            stream=True,
        )

        collected_chunks = []
        collected_messages = []

        for chunk in response:
            collected_chunks.append(chunk)
            chunk_message = chunk["choices"][0]["delta"]
            collected_messages.append(chunk_message)
            self.progress.emit("".join(chunk_message.get("content", "")))

        full_reply = "".join([m.get("content", "") for m in collected_messages])

        messages.append({"role": "assistant", "content": f"{full_reply}"})

    def run(self):
        self.generate_response()
        self.finished.emit()


# Chat Settings Tab
class Tab3(QWidget):
    def __init__(self, parent=None):
        super(Tab3, self).__init__(parent)

        # setting default variables
        global chat_engine
        chat_engine = "gpt-4"

        global tempAmount
        tempAmount = 0.1

        global tokenAmount
        tokenAmount = 10

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

        self.exportButton = QPushButton("Export Chat")
        self.exportButton.clicked.connect(self.export_chat)
        self.engineBox = QComboBox()

        self.engineBox.addItems(model_list)

        self.engineBox.setCurrentText(chat_engine)
        self.engineBox.currentIndexChanged.connect(self.selection_change)

    def selection_change(self):
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

    def export_chat(self):
        try:
            f = open(time.strftime("%Y-%m-%d-%H-%M-%S") + ".txt", "w+")
            # parse json from messages array
            for i in range(len(messages)):
                f.write(f"{messages[i]['role']}: {messages[i]['content']}\n")
            f.close()
        except Exception as e:
            print(f"Error: {e}")

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
        law(self.exportButton, 5, 0)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
