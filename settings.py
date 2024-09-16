from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
                             QLabel, QSpinBox, QTextEdit, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from utils import load_settings, save_settings
from ollama import OllamaAPI

class TestOllamaThread(QThread):
    test_complete = pyqtSignal(bool, str)

    def __init__(self, url, model):
        super().__init__()
        self.url = url
        self.model = model

    def run(self):
        try:
            ollama_api = OllamaAPI(self.url, self.model)
            response = ollama_api.send_request("Test prompt", "This is a test message.", "Hello, Ollama!")
            self.test_complete.emit(True, response)
        except Exception as e:
            self.test_complete.emit(False, str(e))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.initUI()
        self.load_current_settings()

    def initUI(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.ollama_url_input = QLineEdit(self)
        form_layout.addRow("Ollama URL:", self.ollama_url_input)

        self.model_input = QLineEdit(self)
        form_layout.addRow("Model:", self.model_input)

        test_layout = QHBoxLayout()
        self.test_ollama_button = QPushButton("Test Ollama", self)
        self.test_ollama_button.clicked.connect(self.test_ollama)
        test_layout.addWidget(self.test_ollama_button)
        form_layout.addRow("", test_layout)

        self.capture_interval_input = QSpinBox(self)
        self.capture_interval_input.setRange(1, 3600)
        form_layout.addRow("Capture Interval (seconds):", self.capture_interval_input)

        self.my_username_input = QLineEdit(self)
        form_layout.addRow("My Username:", self.my_username_input)

        self.other_usernames_input = QLineEdit(self)
        form_layout.addRow("Other Usernames (comma-separated):", self.other_usernames_input)

        self.prompt_input = QTextEdit(self)
        self.prompt_input.setFixedHeight(100)
        form_layout.addRow("Prompt:", self.prompt_input)

        self.ignored_lines_input = QTextEdit(self)
        self.ignored_lines_input.setFixedHeight(100)
        form_layout.addRow("Ignored Lines Format (one per line):", self.ignored_lines_input)

        layout.addLayout(form_layout)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def load_current_settings(self):
        settings = load_settings()
        self.ollama_url_input.setText(settings['ollama_url'])
        self.model_input.setText(settings['model'])
        self.capture_interval_input.setValue(settings['capture_interval'])
        self.my_username_input.setText(settings['my_username'])
        self.other_usernames_input.setText(", ".join(settings['other_usernames']))
        self.prompt_input.setPlainText(settings['prompt'])
        self.ignored_lines_input.setPlainText("\n".join(settings.get('ignored_lines', [])))

    def save_settings(self):
        new_settings = {
            'ollama_url': self.ollama_url_input.text(),
            'model': self.model_input.text(),
            'capture_interval': self.capture_interval_input.value(),
            'my_username': self.my_username_input.text(),
            'other_usernames': [username.strip() for username in self.other_usernames_input.text().split(',') if username.strip()],
            'prompt': self.prompt_input.toPlainText(),
            'ignored_lines': [line.strip() for line in self.ignored_lines_input.toPlainText().split('\n') if line.strip()]
        }
        save_settings(new_settings)
        self.accept()

    def test_ollama(self):
        url = self.ollama_url_input.text()
        model = self.model_input.text()
        self.test_thread = TestOllamaThread(url, model)
        self.test_thread.test_complete.connect(self.on_test_complete)
        self.test_thread.start()
        QMessageBox.information(self, "Testing Ollama", "Testing connection to Ollama. Please wait...")

    def on_test_complete(self, success, message):
        if success:
            QMessageBox.information(self, "Test Successful", f"Successfully connected to Ollama.\nResponse: {message}")
        else:
            QMessageBox.critical(self, "Test Failed", f"Failed to connect to Ollama.\nError: {message}")