import logging
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QObject
import pyautogui
from utils import load_settings, save_settings, create_new_log_file
from ollama import OllamaAPI
from settings import SettingsDialog
from analyzer import TransparentWindow
from capture_handler import CaptureHandler
from ai_handler import AIHandler

class LogHandler(QObject):
    log_message = pyqtSignal(str)

class ThreadSafeLogger(logging.Handler):
    def __init__(self, log_widget):
        super().__init__()
        self.log_handler = LogHandler()
        self.log_handler.log_message.connect(log_widget.append)

    def emit(self, record):
        msg = self.format(record)
        self.log_handler.log_message.emit(msg)

class PipsChatAnalyserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_analyzing = False
        self.log_file = None
        self.ollama_api = None
        self.ai_handler = None
        self.capture_interval = 30  # seconds
        self.prompt_text = ""
        self.my_username = ""
        self.other_usernames = []
        self.ignored_patterns = []
        self.chat_input_position = None
        self.chat_input_position_display = None
        self.initUI()
        self.load_settings()
        self.init_analyzer()
        self.init_capture_handler()
        self.init_ai_handler()

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
        self.background_prompt.setFixedHeight(4 * self.background_prompt.fontMetrics().lineSpacing())
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
        
        # Chat log
        layout.addWidget(QLabel("Chat log and information"))
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        # Set up logging to the QTextEdit
        self.setup_logging()

        # Last captured line display
        self.last_captured_line = QLineEdit(self)
        self.last_captured_line.setReadOnly(True)
        layout.addWidget(QLabel("Last Captured Line:"))
        layout.addWidget(self.last_captured_line)

        # Chat input position display
        self.chat_input_position_display = QLineEdit(self)
        self.chat_input_position_display.setReadOnly(True)
        layout.addWidget(QLabel("Chat text position:"))
        layout.addWidget(self.chat_input_position_display)

        # Capture, Start, and Stop buttons
        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_analysis)
        button_layout.addWidget(self.capture_button)
        
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_analysis)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('application_log.txt')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Thread-safe handler for QTextEdit
        text_handler = ThreadSafeLogger(self.chat_log)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(text_handler)

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.show()

    def init_capture_handler(self):
        self.capture_handler = CaptureHandler(self.analyzer_window, self.my_username, self.other_usernames, self.ignored_patterns)
        self.capture_handler.capture_complete.connect(self.on_capture_complete)
        self.capture_handler.new_message_detected.connect(self.on_new_message_detected)

    def init_ai_handler(self):
        self.ai_handler = AIHandler(self.ollama_api, self.prompt_text)

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
            self.chat_input_position = pyautogui.Point(x=chat_input_position['x'], y=chat_input_position['y'])
            if self.chat_input_position_display:
                self.chat_input_position_display.setText(f"x={self.chat_input_position.x}, y={self.chat_input_position.y}")
        
        self.background_prompt.setPlainText(self.prompt_text)
        self.my_username_input.setText(self.my_username)
        self.other_usernames_input.setText(", ".join(self.other_usernames))
        
        if self.ai_handler:
            self.ai_handler.set_background_prompt(self.prompt_text)
        
        logging.info(f"Loaded prompt: {self.prompt_text}")
        logging.info(f"Loaded my username: {self.my_username}")
        logging.info(f"Loaded other usernames: {self.other_usernames}")
        logging.info(f"Loaded ignored patterns: {self.ignored_patterns}")
        logging.info(f"Loaded chat input position: {self.chat_input_position}")

    def save_settings(self):
        settings = {
            'prompt': self.background_prompt.toPlainText(),
            'my_username': self.my_username_input.text(),
            'other_usernames': [username.strip() for username in self.other_usernames_input.text().split(',') if username.strip()],
            'ollama_url': self.ollama_api.base_url,
            'model': self.ollama_api.model,
            'capture_interval': self.capture_interval,
            'ignored_lines': self.ignored_patterns,
            'chat_input_position': {'x': self.chat_input_position.x, 'y': self.chat_input_position.y} if self.chat_input_position else {}
        }
        save_settings(settings)
        self.load_settings()  # Reload settings after saving
        QMessageBox.information(self, "Success", "Settings saved successfully.")

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_():
            self.load_settings()

    def capture_analysis(self):
        self.capture_button.setEnabled(False)
        self.log_file = create_new_log_file()
        logging.info(f"Screen capture output saved in: {self.log_file}")
        self.capture_handler.set_log_file(self.log_file)
        self.capture_handler.start_capture()

    @pyqtSlot(list)
    def on_capture_complete(self, processed_lines):
        if processed_lines:
            self.last_captured_line.setText(processed_lines[-1][1])
        self.capture_button.setEnabled(True)

    def start_analysis(self):
        if not self.log_file:
            logging.error("Error: No capture performed. Please capture first.")
            QMessageBox.warning(self, "Error", "No capture performed. Please capture first.")
            return
        
        self.is_analyzing = True
        self.start_button.setEnabled(False)
        logging.info("System: Analysis started")

        if not self.chat_input_position:
            QMessageBox.information(self, "Chat Input Position", "You have 5 seconds to click on the chat input field.")
            QTimer.singleShot(5000, self.set_chat_input_position)
        else:
            self.continuous_analysis()

    def set_chat_input_position(self):
        self.chat_input_position = pyautogui.position()
        self.chat_input_position_display.setText(f"x={self.chat_input_position.x}, y={self.chat_input_position.y}")
        logging.info(f"Chat input position set to: Point(x={self.chat_input_position.x}, y={self.chat_input_position.y})")
        self.continuous_analysis()

    def continuous_analysis(self):
        if self.is_analyzing:
            logging.info(f"{self.capture_interval} sec before next screen refresh")
            QTimer.singleShot(self.capture_interval * 1000, self.capture_handler.start_capture)

    @pyqtSlot(str, str)
    def on_new_message_detected(self, username, message):
        response, error = self.ai_handler.process_new_message(self.log_file, username, message, self.chat_input_position)
        if error:
            QMessageBox.warning(self, "Error", f"An error occurred while processing the AI response: {error}")
        else:
            self.capture_handler.append_to_csv(self.log_file, "ollama_response", "Ollama", response)

    def stop_analysis(self):
        self.is_analyzing = False
        self.start_button.setEnabled(True)
        logging.info("System: Analysis stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyserUI()
    main_window.show()
    sys.exit(app.exec_())