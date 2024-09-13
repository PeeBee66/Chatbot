from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QPlainTextEdit, QLabel,
                             QGroupBox, QFormLayout, QMessageBox, QProgressDialog)
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, Qt
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
        self.setGeometry(200, 200, 400, 300)
        self.settings = QSettings("PipsChat", "ChatAnalyzer")
        self.initUI()
        self.load_settings()

    def initUI(self):
        layout = QVBoxLayout()

        # Ollama API Settings section
        api_group = QGroupBox("Ollama API Settings")
        api_layout = QFormLayout()
        
        self.url_input = QLineEdit()
        api_layout.addRow("Ollama URL and Port:", self.url_input)
        
        self.model_input = QLineEdit()
        api_layout.addRow("Model:", self.model_input)
        
        self.test_server_button = QPushButton("Test Ollama Server")
        self.test_server_button.clicked.connect(self.test_ollama_server)
        api_layout.addRow(self.test_server_button)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Capture Settings section
        capture_group = QGroupBox("Capture Settings")
        capture_layout = QFormLayout()
        
        self.capture_interval = QLineEdit()
        capture_layout.addRow("Capture Interval (seconds):", self.capture_interval)
        
        capture_group.setLayout(capture_layout)
        layout.addWidget(capture_group)

        # Discord chat section
        discord_group = QGroupBox("Discord Chat")
        discord_layout = QVBoxLayout()
        self.discord_enable = QCheckBox("Enable")
        discord_layout.addWidget(self.discord_enable)
        
        ignore_label = QLabel("Ignore users (one per line):")
        discord_layout.addWidget(ignore_label)
        self.ignore_users = QPlainTextEdit()
        discord_layout.addWidget(self.ignore_users)
        
        discord_group.setLayout(discord_layout)
        layout.addWidget(discord_group)

        # Save and Cancel buttons
        button_layout = QVBoxLayout()
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_settings(self):
        self.url_input.setText(self.settings.value("ollama_url", "http://localhost:11434"))
        self.model_input.setText(self.settings.value("model", "llama2"))
        self.capture_interval.setText(str(self.settings.value("capture_interval", 15)))
        self.discord_enable.setChecked(self.settings.value("discord_enable", False, type=bool))
        self.ignore_users.setPlainText("\n".join(self.settings.value("ignore_users", [])))

    def save_settings(self):
        try:
            self.settings.setValue("ollama_url", self.url_input.text())
            self.settings.setValue("model", self.model_input.text())
            self.settings.setValue("capture_interval", int(self.capture_interval.text()))
            self.settings.setValue("discord_enable", self.discord_enable.isChecked())
            self.settings.setValue("ignore_users", self.ignore_users.toPlainText().split('\n'))
            
            self.settings.sync()
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please ensure all fields are filled correctly.")

    def get_settings(self):
        return {
            'ollama_url': self.settings.value("ollama_url", "http://localhost:11434"),
            'model': self.settings.value("model", "llama2"),
            'capture_interval': int(self.settings.value("capture_interval", 15)),
            'discord_enable': self.settings.value("discord_enable", False, type=bool),
            'ignore_users': self.settings.value("ignore_users", [])
        }

    def test_ollama_server(self):
        url = self.url_input.text()
        model = self.model_input.text()

        progress = QProgressDialog("Testing connection to Ollama server...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Testing Ollama Server")
        progress.setAutoClose(True)
        progress.setCancelButton(None)
        progress.show()

        self.test_thread = TestOllamaThread(url, model)
        self.test_thread.test_complete.connect(self.on_test_complete)
        self.test_thread.finished.connect(progress.close)
        self.test_thread.start()

    def on_test_complete(self, success, message):
        if success:
            QMessageBox.information(self, "Server Test", f"Successfully connected to Ollama server.\nResponse: {message}")
        else:
            QMessageBox.critical(self, "Server Test Failed", f"Failed to connect to Ollama server.\nError: {message}")

def load_settings():
    settings = QSettings("PipsChat", "ChatAnalyzer")
    return {
        'ollama_url': settings.value("ollama_url", "http://localhost:11434"),
        'model': settings.value("model", "llama2"),
        'capture_interval': int(settings.value("capture_interval", 15)),
        'discord_enable': settings.value("discord_enable", False, type=bool),
        'ignore_users': settings.value("ignore_users", [])
    }