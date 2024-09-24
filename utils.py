import json
import os
import csv
import logging
import re
from PyQt5.QtCore import QSettings, QObject, pyqtSignal
from datetime import datetime

def load_settings():
    settings = QSettings("PipsChat", "ChatAnalyzer")
    try:
        with open('settings.json', 'r') as f:
            file_settings = json.load(f)
    except FileNotFoundError:
        file_settings = {}
    
    return {
        'ollama_url': file_settings.get('ollama_url') or settings.value("ollama_url", "http://localhost:11434"),
        'model': file_settings.get('model') or settings.value("model", "llama2"),
        'capture_interval': int(file_settings.get('capture_interval') or settings.value("capture_interval", 15)),
        'prompt': file_settings.get('prompt') or settings.value("prompt", ""),
        'my_username': file_settings.get('my_username') or settings.value("my_username", ""),
        'other_usernames': file_settings.get('other_usernames') or settings.value("other_usernames", []),
        'ignored_lines': file_settings.get('ignored_lines') or settings.value("ignored_lines", []),
        'chat_input_position': file_settings.get('chat_input_position') or settings.value("chat_input_position", {})
    }

def save_settings(settings):
    q_settings = QSettings("PipsChat", "ChatAnalyzer")
    for key, value in settings.items():
        q_settings.setValue(key, value)
    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

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
        writer.writerow(["ID", "Conversation", "Username", "Message"])
    
    return log_file

def append_to_csv(log_file, conversation_type, username, message):
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        with open(log_file, mode='r', newline='', encoding='utf-8') as readfile:
            lines = list(csv.reader(readfile))
            last_id = int(lines[-1][0]) if len(lines) > 1 else 0
        
        writer.writerow([f"{last_id + 1:04d}", conversation_type, username, message])

def get_last_messages(log_file, n=10):
    try:
        with open(log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            messages = list(reader)
            return [(row[2], row[3]) for row in messages[-n:]]
    except Exception as e:
        logging.error(f"Error reading last messages from CSV: {str(e)}")
        return []

def is_ignored_line(line, ignored_patterns):
    # Check if the line matches any of the ignored patterns
    for pattern in ignored_patterns:
        if re.search(pattern, line):
            return True
    
    # Check for date formats
    date_patterns = [
        r"\w+,\s+\w+\s+\d{1,2}(st|nd|rd|th)\s+v",  # e.g., "Friday, September 13th v"
        r"Today\s+v",
        r"\w+\s+\d{1,2}(st|nd|rd|th),\s+\d{4}"  # e.g., "September 16th, 2024"
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, line):
            return True
    
    return False

class QTextEditLogger(QObject, logging.Handler):
    log_message = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.log_message.emit(msg)

def setup_logging(log_widget):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler('application_log.txt')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Widget handler
    widget_handler = QTextEditLogger(log_widget)
    widget_handler.log_message.connect(log_widget.append)
    logger.addHandler(widget_handler)

    return logger

def process_captured_text(text, my_username, other_usernames, ignored_patterns):
    logging.debug(f"Processing captured text: {text[:100]}...")  # Log first 100 characters
    lines = text.split('\n')
    processed_lines = []
    current_username = None

    for line in lines:
        line = line.strip()
        if not line or is_ignored_line(line, ignored_patterns):
            continue

        for username in [my_username] + other_usernames:
            if line.lower().startswith(username.lower()):
                current_username = username
                message = line[len(username):].strip()
                if message.startswith(':'):
                    message = message[1:].strip()
                processed_lines.append((current_username, message))
                break
        else:
            if current_username:
                processed_lines.append((current_username, line))

    logging.debug(f"Processed {len(processed_lines)} lines")
    return processed_lines