import logging
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QMessageBox, 
                             QTextEdit, QApplication, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSlot
from utils import load_settings, save_settings, setup_logging
from ollama import OllamaAPI
from settings import SettingsDialog
from analyzer import TransparentWindow
from capture_handler import CaptureHandler
from start_analyzer import StartAnalyzer
from ai_handler import AIHandler
from chat_position_handler import ChatPositionHandler

class PipsChatAnalyserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ollama_api = None
        self.ai_handler = None
        self.capture_interval = 30  # seconds
        self.prompt_text = ""
        self.my_username = ""
        self.other_usernames = []
        self.ignored_patterns = []
        self.chat_position_handler = ChatPositionHandler()
        self.log_file = None
        self.initUI()
        self.setup_logging()
        self.load_settings()
        self.init_analyzer()
        self.init_capture_handler()
        self.init_ai_handler()
        self.init_start_analyzer()

    def initUI(self):
        self.setWindowTitle("PIPS CHAT ANALYSER")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Background Prompt
        layout.addWidget(QLabel("Background Prompt"))
        self.background_prompt = QTextEdit(self)
        self.background_prompt.setPlainText(self.prompt_text)
        self.background_prompt.setFixedHeight(100)
        layout.addWidget(self.background_prompt)

        # Save and Settings buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)
        layout.addLayout(button_layout)
        
        # Username inputs
        username_layout = QHBoxLayout()
        self.my_username_input = QLineEdit(self)
        self.my_username_input.setPlaceholderText("My username")
        username_layout.addWidget(QLabel("My Username:"))
        username_layout.addWidget(self.my_username_input)
        
        self.other_usernames_input = QLineEdit(self)
        self.other_usernames_input.setPlaceholderText("Other usernames (comma-separated)")
        username_layout.addWidget(QLabel("Other Usernames:"))
        username_layout.addWidget(self.other_usernames_input)
        layout.addLayout(username_layout)
        
        # Capture Interval
        interval_layout = QHBoxLayout()
        self.capture_interval_input = QSpinBox(self)
        self.capture_interval_input.setRange(1, 3600)
        self.capture_interval_input.setValue(self.capture_interval)
        interval_layout.addWidget(QLabel("Capture Interval (seconds):"))
        interval_layout.addWidget(self.capture_interval_input)
        layout.addLayout(interval_layout)
        
        # Chat log
        layout.addWidget(QLabel("Chat log and information"))
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        # Last captured line display
        self.last_captured_line = QLineEdit(self)
        self.last_captured_line.setReadOnly(True)
        layout.addWidget(QLabel("Last Captured Line:"))
        layout.addWidget(self.last_captured_line)

        # Chat Input Position
        chat_position_layout = QHBoxLayout()
        self.chat_x_input = QLineEdit(self)
        self.chat_y_input = QLineEdit(self)
        self.set_chat_position_button = QPushButton("Set Chat Position", self)
        self.set_chat_position_button.clicked.connect(self.chat_position_handler.set_chat_position)
        chat_position_layout.addWidget(QLabel("Chat X:"))
        chat_position_layout.addWidget(self.chat_x_input)
        chat_position_layout.addWidget(QLabel("Chat Y:"))
        chat_position_layout.addWidget(self.chat_y_input)
        chat_position_layout.addWidget(self.set_chat_position_button)
        layout.addLayout(chat_position_layout)

        # Capture, Start, and Stop buttons
        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_analysis)
        button_layout.addWidget(self.capture_button)
        
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_analysis)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_analysis)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        # Connect the position_set signal
        self.chat_position_handler.position_set.connect(self.update_chat_position_inputs)

    def setup_logging(self):
        self.logger = setup_logging(self.chat_log)

    def load_settings(self):
        settings = load_settings()
        self.ollama_api = OllamaAPI(settings['ollama_url'], settings['model'])
        self.capture_interval = settings['capture_interval']
        self.prompt_text = settings.get('prompt', '')
        self.my_username = settings.get('my_username', '')
        self.other_usernames = settings.get('other_usernames', [])
        self.ignored_patterns = settings.get('ignored_lines', [])
        chat_input_position = settings.get('chat_input_position', {})
        if chat_input_position:
            self.chat_position_handler.set_chat_position_from_settings(chat_input_position['x'], chat_input_position['y'])
            self.update_chat_position_inputs(chat_input_position['x'], chat_input_position['y'])
        
        self.background_prompt.setPlainText(self.prompt_text)
        self.my_username_input.setText(self.my_username)
        self.other_usernames_input.setText(", ".join(self.other_usernames))
        self.capture_interval_input.setValue(self.capture_interval)
        
        if self.ai_handler:
            self.ai_handler.set_background_prompt(self.prompt_text)
        
        logging.info(f"Settings loaded successfully")

    def save_settings(self):
        settings = {
            'prompt': self.background_prompt.toPlainText(),
            'my_username': self.my_username_input.text(),
            'other_usernames': [username.strip() for username in self.other_usernames_input.text().split(',') if username.strip()],
            'ollama_url': self.ollama_api.base_url,
            'model': self.ollama_api.model,
            'capture_interval': self.capture_interval_input.value(),
            'ignored_lines': self.ignored_patterns,
            'chat_input_position': {'x': int(self.chat_x_input.text()), 'y': int(self.chat_y_input.text())} if self.chat_position_handler.has_position() else {}
        }
        save_settings(settings)
        self.load_settings()  # Reload settings after saving
        QMessageBox.information(self, "Success", "Settings saved successfully.")

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_():
            self.load_settings()

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.show()

    def init_capture_handler(self):
        self.capture_handler = CaptureHandler(self.analyzer_window, self.my_username, self.other_usernames, self.ignored_patterns)

    def init_ai_handler(self):
        self.ai_handler = AIHandler(self.ollama_api, self.prompt_text, self.chat_position_handler)
        self.ai_handler.response_ready.connect(self.handle_ollama_response)

    def init_start_analyzer(self):
        self.start_analyzer = StartAnalyzer(self.analyzer_window, self.capture_handler, self.ai_handler, self.chat_position_handler, self.capture_interval)
        self.start_analyzer.analysis_complete.connect(self.on_analysis_complete)
        self.start_analyzer.ollama_response_ready.connect(self.handle_ollama_response)
        self.start_analyzer.capture_complete.connect(self.on_capture_complete)

    def set_log_file(self, log_file):
        self.log_file = log_file
        if self.ai_handler:
            self.ai_handler.set_log_file(log_file)

    def capture_analysis(self):
        if not self.check_settings():
            return
        
        self.capture_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        log_file = self.start_analyzer.capture_restart()
        self.set_log_file(log_file)  # Set the log file after capture

    def start_analysis(self):
        try:
            self.start_analyzer.start_analysis()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.capture_button.setEnabled(False)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def stop_analysis(self):
        self.start_analyzer.stop_analysis()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(True)

    def check_settings(self):
        settings = load_settings()
        empty_settings = [key for key, value in settings.items() if not value]
        if empty_settings:
            QMessageBox.warning(self, "Empty Settings", f"The following settings are empty: {', '.join(empty_settings)}")
            return False
        return True

    @pyqtSlot(bool)
    def on_capture_complete(self, success):
        if success:
            self.start_button.setEnabled(True)
            logging.info("Capture completed successfully")
        else:
            QMessageBox.warning(self, "Capture Failed", "Failed to capture screen. Please try again.")
        self.capture_button.setEnabled(True)

    @pyqtSlot(list, bool)
    def on_analysis_complete(self, new_text, waiting_for_ollama):
        if new_text:
            self.last_captured_line.setText(new_text[-1][1])
        if waiting_for_ollama:
            self.chat_log.append("Waiting for Ollama response...")
        else:
            self.chat_log.append("Analysis cycle completed.")

    @pyqtSlot(str, str)
    def handle_ollama_response(self, response, error):
        if error:
            QMessageBox.warning(self, "Error", f"An error occurred while processing the AI response: {error}")
        else:
            self.chat_log.append(f"Ollama response received: {response[:50]}...")

    @pyqtSlot(int, int)
    def update_chat_position_inputs(self, x, y):
        self.chat_x_input.setText(str(x))
        self.chat_y_input.setText(str(y))

if __name__ == "__main__":
    app = QApplication([])
    main_window = PipsChatAnalyserUI()
    main_window.show()
    app.exec_()