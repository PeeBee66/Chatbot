import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout,
                             QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from analyzer import TransparentWindow
from settings import SettingsDialog
from ollama import OllamaAPI
import pyautogui

class PipsChatAnalyser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_analyzing = False
        self.init_analyzer()
        self.settings_dialog = SettingsDialog(self)
        self.load_settings()
        self.captured_text = ""
        self.last_ai_message = ""
        self.last_scanned_text = ""
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.scan_for_changes)
        self.last_processed_messages = []

    def initUI(self):
        self.setWindowTitle("PIPS CHAT ANALYSER")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)

        # Settings button (top-right corner)
        self.settings_button = QPushButton(self)
        self.settings_button.setIcon(QIcon('cog.png'))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings)
        main_layout.addWidget(self.settings_button, 0, 1, 1, 1, Qt.AlignRight | Qt.AlignTop)

        # Background prompt text box with default prompt
        self.background_prompt = QTextEdit(self)
        default_prompt = "You are a helpful assistant. Keep your responses concise, using no more than 2 sentences."
        self.background_prompt.setPlainText(default_prompt)
        main_layout.addWidget(self.background_prompt, 1, 0, 1, 2)

        # Chat log
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        main_layout.addWidget(self.chat_log, 2, 0, 1, 2)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_analysis)
        button_layout.addWidget(self.capture_button)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_analysis)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.pause_analysis)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_analysis)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        main_layout.addWidget(button_widget, 3, 0, 1, 2)

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.text_captured.connect(self.update_captured_text)
        self.analyzer_window.show()

    def open_settings(self):
        if self.settings_dialog.exec_():
            self.load_settings()

    def load_settings(self):
        settings = self.settings_dialog.get_settings()
        self.ollama_api = OllamaAPI(
            settings.get('ollama_url', "http://ollama:11434"),
            settings.get('model', "llama3.1:latest")
        )
        self.log_message(f"Settings loaded: Ollama URL: {settings.get('ollama_url')}, Model: {settings.get('model')}")

    def log_message(self, message):
        self.chat_log.append(message)
        print(message)  # Also print to console for debugging

    def capture_analysis(self):
        self.log_message("System: Capture initiated")
        self.analyzer_window.start_capture()
        self.capture_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def update_captured_text(self, text):
        self.captured_text = text
        self.log_message(f"Captured text:\n{text}")
        self.analyzer_window.stop_capture()

    def start_analysis(self):
        if not self.captured_text:
            self.log_message("Error: No text captured. Please capture text first.")
            return
        
        msg_box = QMessageBox()
        msg_box.setText("Click OK and move your cursor to the messaging prompt. The analysis will start in 3 seconds.")
        msg_box.exec_()

        QTimer.singleShot(3000, self.initiate_conversation)

    def initiate_conversation(self):
        self.is_analyzing = True
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.log_message("System: Analysis started")
        
        if self.ollama_api is None:
            self.log_message("Error: Ollama API not initialized. Please check settings.")
            return
        
        system_prompt = self.background_prompt.toPlainText()
        response = self.ollama_api.send_request(
            system_prompt,
            "This is the chat history from a conversation. Please analyze it and start a conversation based on it.",
            self.captured_text
        )
        self.log_message(f"Ollama: {response}")
        self.type_and_send_message(response)
        self.last_ai_message = response
        self.last_scanned_text = self.captured_text + "\n" + response
        self.scan_timer.start(15000)  # Start scanning every 15 seconds

    def scan_for_changes(self):
        self.analyzer_window.start_capture()
        QTimer.singleShot(1000, self.process_scanned_text)  # Give it 1 second to capture
  
    def process_scanned_text(self):
        self.analyzer_window.stop_capture()
        new_text = self.captured_text

        # Split the text into individual messages
        messages = [msg.strip() for msg in new_text.split('\n') if msg.strip()]

        # Find new messages
        new_messages = [msg for msg in messages if msg not in self.last_processed_messages]

        if not new_messages:
            self.log_message("No change detected in chat.")
            return

        # Process each new message
        for message in new_messages:
            if message != self.last_ai_message:
                self.log_message(f"New content detected: {message}")
                self.continue_conversation(message)

        # Update the last processed messages
        self.last_processed_messages = messages

    def continue_conversation(self, new_content):
        if self.ollama_api is None:
            self.log_message("Error: Ollama API not initialized. Please check settings.")
            return
        
        system_prompt = self.background_prompt.toPlainText()
        response = self.ollama_api.send_request(
            system_prompt,
            "Continue the conversation based on the new message.",
            new_content
        )
        self.log_message(f"Ollama: {response}")
        self.type_and_send_message(response)
        self.last_ai_message = response
        self.last_processed_messages.append(response)

    def type_and_send_message(self, message):
        pyautogui.typewrite(message)
        pyautogui.press('enter')

    def pause_analysis(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.pause_button.setText("Resume")
            self.log_message("System: Analysis paused")
            self.scan_timer.stop()
        else:
            self.is_analyzing = True
            self.pause_button.setText("Pause")
            self.log_message("System: Analysis resumed")
            self.scan_timer.start(15000)

    def stop_analysis(self):
        self.is_analyzing = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(True)
        self.pause_button.setText("Pause")
        self.log_message("System: Analysis stopped")
        self.captured_text = ""
        self.last_ai_message = ""
        self.last_scanned_text = ""
        self.scan_timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyser()
    main_window.show()
    sys.exit(app.exec_())