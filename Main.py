import sys
import os
import csv
import logging
import time
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import pyautogui
from ollama import OllamaAPI
from analyzer import TransparentWindow
from settings import SettingsDialog, load_settings

# Configure logging
logging.basicConfig(filename='application_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class CaptureThread(QThread):
    capture_complete = pyqtSignal(str)

    def __init__(self, analyzer_window):
        super().__init__()
        self.analyzer_window = analyzer_window

    def run(self):
        text = self.analyzer_window.capture_screen()
        self.capture_complete.emit(text)

class AnalysisThread(QThread):
    analysis_complete = pyqtSignal(str)

    def __init__(self, log_file, background_prompt, ollama_api):
        super().__init__()
        self.log_file = log_file
        self.background_prompt = background_prompt
        self.ollama_api = ollama_api

    def run(self):
        response = self.start_conversation()
        self.analysis_complete.emit(response)

    def start_conversation(self):
        try:
            with open(self.log_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                chat_history = [f"{row[1]}: {row[2]}" for row in reader]
            
            chat_history_text = "\n".join(chat_history)
            prompt = f"{self.background_prompt}\n\n{chat_history_text}"
            logging.info("Contacting Ollama server: Please wait for response (this may take a bit depending on AI assistant speeds)")
            response = self.ollama_api.send_request(self.background_prompt, "Please respond to the following conversation.", chat_history_text)
            logging.info("Received response from Ollama server")
            
            return response
        except Exception as e:
            logging.error(f"Error starting conversation: {str(e)}")
            return ""

class PipsChatAnalyser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_analyzing = False
        self.init_analyzer()
        self.captured_text = ""
        self.log_file = None
        self.response = None
        self.ollama_api = None
        self.load_settings()
        self.capture_interval = 30  # seconds
    
    def initUI(self):
        self.setWindowTitle("PIPS CHAT ANALYSER")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.background_prompt = QTextEdit(self)
        self.background_prompt.setPlainText("You are a helpful assistant. Please keep responses concise.")
        layout.addWidget(self.background_prompt)
        
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        # Set up logging to the QTextEdit
        logTextBox = QTextEditLogger(self.chat_log)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_analysis)
        layout.addWidget(self.capture_button)
        
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_analysis)
        layout.addWidget(self.stop_button)

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

    def init_analyzer(self):
        self.analyzer_window = TransparentWindow()
        self.analyzer_window.show()

    def load_settings(self):
        settings = load_settings()
        self.ollama_api = OllamaAPI(settings['ollama_url'], settings['model'])
        self.capture_interval = settings['capture_interval']

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_():
            self.load_settings()

    def capture_analysis(self):
        logging.info("System: Capture initiated")
        self.capture_button.setEnabled(False)

        self.log_file = create_new_log_file()
        logging.info(f"Screen capture output saved in: {self.log_file}")

        self.capture_thread = CaptureThread(self.analyzer_window)
        self.capture_thread.capture_complete.connect(self.on_capture_complete)
        self.capture_thread.start()

    def on_capture_complete(self, text):
        if text:
            lines = self.process_captured_text(text)
            for line in lines:
                append_to_csv(self.log_file, "first_conversation", line)
            logging.info("Text added to chat log.")
        else:
            logging.info("No text captured.")
        self.capture_button.setEnabled(True)

    def process_captured_text(self, text):
        lines = text.split('\n')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line and not self.is_time_stamp(line):
                # Replace '|' with 'I' at the beginning of the line
                line = re.sub(r'^[|]', 'I', line)
                # Replace isolated '|' with 'I'
                line = re.sub(r'\s[|]\s', ' I ', line)
                processed_lines.append(line)
        return processed_lines

    def is_time_stamp(self, line):
        # Check if the line starts or ends with a time stamp (e.g., "3:45 PM" or "10:30 AM")
        time_pattern = r'^\d{1,2}:\d{2}\s?(?:AM|PM)|(?:AM|PM)\s?\d{1,2}:\d{2}$'
        return re.match(time_pattern, line.strip())

    def start_analysis(self):
        if not self.log_file:
            logging.error("Error: No capture performed. Please capture first.")
            return
        
        self.is_analyzing = True
        self.start_button.setEnabled(False)
        logging.info("System: Analysis started")

        QMessageBox.information(self, "Chat Input Position", "Please move your cursor to the chat input field and press OK.")
        self.chat_input_position = pyautogui.position()
        logging.info(f"Chat input position set to: {self.chat_input_position}")
        
        self.analysis_thread = AnalysisThread(self.log_file, self.background_prompt.toPlainText(), self.ollama_api)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()

    def on_analysis_complete(self, response):
        logging.info(f"Ollama's response: {response}")
        logging.info("Ollama chat added to chat log.")
        self.response = response
        
        self.write_response_to_chat(response)
        
        append_to_csv(self.log_file, "ollama_response", response)
        self.continuous_analysis()

    def continuous_analysis(self):
        if self.is_analyzing:
            logging.info(f"{self.capture_interval} sec before next screen refresh")
            QTimer.singleShot(self.capture_interval * 1000, self.check_for_new_messages)

    def check_for_new_messages(self):
        logging.info("Capturing screen for updated text")
        self.capture_thread = CaptureThread(self.analyzer_window)
        self.capture_thread.capture_complete.connect(self.on_new_capture_complete)
        self.capture_thread.start()

    def on_new_capture_complete(self, text):
        if text:
            new_messages = self.get_new_messages(text)
            if new_messages:
                for message in new_messages:
                    logging.info(f"New user message detected: {message}")
                    append_to_csv(self.log_file, "user_message", message)
                    self.process_new_message(message)
            else:
                logging.info("No new user messages detected.")
        else:
            logging.info("No new text captured.")
        
        if self.is_analyzing:
            self.continuous_analysis()

    def get_new_messages(self, captured_text):
        existing_messages = set()
        with open(self.log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                existing_messages.add(row[2].strip())

        new_messages = []
        for line in self.process_captured_text(captured_text):
            if line not in existing_messages:
                new_messages.append(line)
                existing_messages.add(line)

        return new_messages

    def process_new_message(self, message):
        logging.info("Contacting Ollama server: Please wait for response (this may take a bit depending on AI assistant speeds)")
        response = self.ollama_api.send_request(self.background_prompt.toPlainText(), 
                                                "Please respond to the following message:", 
                                                message)
        logging.info("Received response from Ollama server")
        logging.info(f"Ollama's response: {response}")
        append_to_csv(self.log_file, "ollama_response", response)
        
        self.write_response_to_chat(response)

    def write_response_to_chat(self, response):
        if self.chat_input_position:
            original_position = pyautogui.position()
            pyautogui.click(self.chat_input_position)
            time.sleep(0.5)  # Wait for the click to register
            pyautogui.typewrite(response)
            time.sleep(0.5)  # Wait for typing to complete
            pyautogui.press('enter')
            time.sleep(0.5)  # Wait for enter to register
            pyautogui.moveTo(original_position)  # Move cursor back to original position

    def stop_analysis(self):
        self.is_analyzing = False
        self.start_button.setEnabled(True)
        logging.info("System: Analysis stopped")

def create_new_log_file():
    log_folder = './logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    i = 1
    while os.path.exists(f"{log_folder}/chatlog{i:04d}.csv"):
        i += 1
    
    log_file = f"{log_folder}/chatlog{i:04d}.csv"
    
    with open(log_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Conversation", "Message"])
    
    return log_file

def append_to_csv(log_file, conversation_type, message):
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        with open(log_file, mode='r', newline='', encoding='utf-8') as readfile:
            lines = list(csv.reader(readfile))
            last_id = int(lines[-1][0]) if len(lines) > 1 else 0
        
        writer.writerow([f"{last_id + 1:04d}", conversation_type, message])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyser()
    main_window.show()
    sys.exit(app.exec_())