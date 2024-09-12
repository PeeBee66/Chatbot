from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QPlainTextEdit, QLabel,
                             QGroupBox, QFormLayout)
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)
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
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Discord chat section
        discord_group = QGroupBox("Discord Chat")
        discord_layout = QVBoxLayout()
        self.discord_enable = QCheckBox("Enable")
        discord_layout.addWidget(self.discord_enable)
        
        ignore_label = QLabel("Ignore users:")
        discord_layout.addWidget(ignore_label)
        self.ignore_users = QPlainTextEdit()
        discord_layout.addWidget(self.ignore_users)
        
        discord_group.setLayout(discord_layout)
        layout.addWidget(discord_group)

        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.url_input.setText(settings.get('ollama_url', "http://ollama:11434"))
            self.model_input.setText(settings.get('model', "llama3.1:latest"))
            self.discord_enable.setChecked(settings.get('discord_enable', False))
            self.ignore_users.setPlainText("\n".join(settings.get('ignore_users', [])))
        except FileNotFoundError:
            self.url_input.setText("http://ollama:11434")
            self.model_input.setText("llama3.1:latest")

    def save_settings(self):
        settings = self.get_settings()
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.accept()

    def get_settings(self):
        return {
            'ollama_url': self.url_input.text() or "http://ollama:11434",
            'model': self.model_input.text() or "llama3.1:latest",
            'discord_enable': self.discord_enable.isChecked(),
            'ignore_users': self.ignore_users.toPlainText().split('\n')
        }