import os
import csv
import logging
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer
import pyautogui
from capture import CaptureThread
from analysis import AnalysisThread
from utils import load_settings, save_settings, create_new_log_file, append_to_csv, QTextEditLogger, setup_logging, process_captured_text
from ollama import OllamaAPI
from settings import SettingsDialog
from ollama_handler import handle_ollama_response
from analyzer import TransparentWindow  # Make sure this import is present

class PipsChatAnalyserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_analyzing = False
        self.captured_text = ""
        self.log_file = None
        self.response = None
        self.ollama_api = None
        self.capture_interval = 30  # seconds
        self.prompt_text = ""
        self.my_username = ""
        self.other_usernames = []
        self.ignored_patterns = []
        self.chat_input_position = None
        self.load_settings()
        self.initUI()
        self.init_analyzer()

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
        self.my_username_input.setText(self.my_username)
        self.my_username_input.setPlaceholderText("My username")
        username_layout.addWidget(QLabel("My Username:"))
        username_layout.addWidget(self.my_username_input)
        
        self.other_usernames_input = QLineEdit(self)
        self.other_usernames_input.setText(", ".join(self.other_usernames))
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
        setup_logging(self.chat_log)

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

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.show()

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
            self.chat_input_position_display.setText(f"x={self.chat_input_position.x}, y={self.chat_input_position.y}")
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
            self.background_prompt.setPlainText(self.prompt_text)
            self.my_username_input.setText(self.my_username)
            self.other_usernames_input.setText(", ".join(self.other_usernames))

    def capture_analysis(self):
        logging.info("System: Capture initiated")
        self.capture_button.setEnabled(False)

        self.log_file = create_new_log_file()
        logging.info(f"Screen capture output saved in: {self.log_file}")

        self.capture_thread = CaptureThread(self.analyzer_window, self.my_username, self.other_usernames, self.ignored_patterns)
        self.capture_thread.capture_complete.connect(self.on_capture_complete)
        self.capture_thread.start()

    def on_capture_complete(self, processed_lines):
        if processed_lines:
            for username, message in processed_lines:
                append_to_csv(self.log_file, "first_conversation", username, message)
            self.last_captured_line.setText(processed_lines[-1][1])
            logging.info(f"Text added to chat log. Last line: {processed_lines[-1][1]}")
        else:
            logging.info("No text captured.")
        self.capture_button.setEnabled(True)

    def start_analysis(self):
        if not self.log_file:
            logging.error("Error: No capture performed. Please capture first.")
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
            QTimer.singleShot(self.capture_interval * 1000, self.check_for_new_messages)

    def check_for_new_messages(self):
        logging.info("Capturing screen for updated text")
        self.capture_thread = CaptureThread(self.analyzer_window, self.my_username, self.other_usernames, self.ignored_patterns)
        self.capture_thread.capture_complete.connect(self.on_capture_complete)  # Changed from on_new_capture_complete
        self.capture_thread.start()

    def on_capture_complete(self, processed_lines):
        logging.debug(f"Received processed lines: {processed_lines}")
        if processed_lines:
            new_messages = self.get_new_messages(processed_lines)
            if new_messages:
                for username, message in new_messages:
                    logging.info(f"New user message detected: {username}: {message}")
                    append_to_csv(self.log_file, "user_message", username, message)
                
                last_message = new_messages[-1]
                if last_message[0] in self.other_usernames:
                    self.process_new_message(last_message[0], last_message[1])
                
                self.last_captured_line.setText(new_messages[-1][1])
            else:
                logging.info("No new user messages detected.")
        else:
            logging.warning("No processed lines received")
        
        if self.is_analyzing:
            self.continuous_analysis()

    def get_new_messages(self, processed_lines):
        existing_messages = set()
        with open(self.log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                existing_messages.add((row[2], row[3]))  # username, message

        new_messages = []
        for username, message in processed_lines:
            if (username, message) not in existing_messages:
                new_messages.append((username, message))
                existing_messages.add((username, message))

        return new_messages
    
    def process_new_message(self, username, message):
        # Get all messages from the CSV
        with open(self.log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            all_messages = list(reader)

        # Construct the conversation history
        conversation_history = [f"{row[2]}: {row[3]}" for row in all_messages]
        
        # Construct the system prompt
        system_prompt = f"{self.background_prompt.toPlainText()}\n\nCurrent chat:\n" + "\n".join(conversation_history)

        # Get the last messages from the triggering user
        user_messages = [msg for msg in reversed(all_messages) if msg[2] == username]
        last_user_conversation = "\n".join([f"{msg[2]}: {msg[3]}" for msg in user_messages])

        # Use the new OllamaResponseHandler
        response, error = handle_ollama_response(
            self,
            self.ollama_api,
            system_prompt,
            f"Please respond to the following conversation from {username}:",
            last_user_conversation,
            self.chat_input_position
        )

        if error:
            logging.error(f"Error in Ollama response: {error}")
            QMessageBox.warning(self, "Error", f"An error occurred while processing the AI response: {error}")
        else:
            logging.info(f"Ollama's response: {response}")
            append_to_csv(self.log_file, "ollama_response", "Ollama", response)

    def stop_analysis(self):
        self.is_analyzing = False
        self.start_button.setEnabled(True)
        logging.info("System: Analysis stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyserUI()
    main_window.show()
    sys.exit(app.exec_())