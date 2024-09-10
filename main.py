import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLineEdit, QLabel, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

class TransparentTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 128);")

class ChatBotInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Bot Interface POC")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top buttons
        top_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Prompt")
        self.setting_button = QPushButton("Setting")

        top_layout.addWidget(self.start_button)
        top_layout.addWidget(self.stop_button)
        top_layout.addWidget(self.prompt_input)
        top_layout.addWidget(self.setting_button)

        main_layout.addLayout(top_layout)

        # Main content area with splitters
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top row splitter
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.chat_history = TransparentTextEdit()
        self.chat_history.setPlaceholderText("TRANSPARENT FOR READING THE HISTORY OF THE CHAT")
        self.rewritten_history = QTextEdit()
        self.rewritten_history.setPlaceholderText("REWRITING THE HOSTPORY OF THE CHAT")
        top_splitter.addWidget(self.chat_history)
        top_splitter.addWidget(self.rewritten_history)

        # Bottom row splitter
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.transparent_area = TransparentTextEdit()
        self.transparent_area.setPlaceholderText("TRASPERENT")
        self.proposed_reply = QTextEdit()
        self.proposed_reply.setPlaceholderText("PROPOSED REPLY TEXT")
        bottom_splitter.addWidget(self.transparent_area)
        bottom_splitter.addWidget(self.proposed_reply)

        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_splitter)

        main_layout.addWidget(main_splitter)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        self.rewrite_button = QPushButton("RE WRITE")
        self.copy_button = QPushButton("COPY")
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.rewrite_button)
        bottom_layout.addWidget(self.copy_button)

        main_layout.addLayout(bottom_layout)

        # Connect buttons to functions
        self.start_button.clicked.connect(self.start_process)
        self.stop_button.clicked.connect(self.stop_process)
        self.setting_button.clicked.connect(self.open_settings)
        self.rewrite_button.clicked.connect(self.rewrite_text)
        self.copy_button.clicked.connect(self.copy_text)

        # Timer for simulating real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rewritten_history)

    def start_process(self):
        print("Start button clicked")
        self.timer.start(1000)  # Update every second

    def stop_process(self):
        print("Stop button clicked")
        self.timer.stop()

    def open_settings(self):
        print("Settings button clicked")

    def rewrite_text(self):
        print("Rewrite button clicked")

    def copy_text(self):
        print("Copy button clicked")

    def update_rewritten_history(self):
        current_text = self.chat_history.toPlainText()
        self.rewritten_history.setPlainText(current_text.upper())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatBotInterface()
    window.show()
    sys.exit(app.exec())
