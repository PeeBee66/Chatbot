import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout,
                             QDialog, QLineEdit, QCheckBox, QPlainTextEdit, QLabel, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QTimer
from analyzer import TransparentWindow

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Ollama API String section
        api_group = QGroupBox("Ollama API Settings")
        api_layout = QFormLayout()
        self.api_input = QLineEdit()
        api_layout.addRow("API String:", self.api_input)
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

        self.setLayout(layout)

class PipsChatAnalyser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_analyzing = False
        self.init_analyzer()
        self.settings_dialog = None

    def initUI(self):
        self.setWindowTitle("PIPS CHAT ANALYSER")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Settings button
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        # Chat log
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        # Start and Stop buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_analysis)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.text_captured.connect(self.update_log)
        self.analyzer_window.show()

    def open_settings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show()

    def start_analysis(self):
        self.is_analyzing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_message("System: Analysis started")
        self.analyzer_window.start_capture()

    def stop_analysis(self):
        self.is_analyzing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_message("System: Analysis stopped")
        self.analyzer_window.stop_capture()

    def log_message(self, message):
        self.chat_log.append(message)

    def update_log(self, text):
        self.log_message(f"Captured: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyser()
    main_window.show()
    sys.exit(app.exec_())
