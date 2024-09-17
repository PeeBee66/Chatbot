import logging
import csv
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from capture import CaptureThread
from utils import append_to_csv

class CaptureHandler(QObject):
    capture_complete = pyqtSignal(list)
    new_message_detected = pyqtSignal(str, str)

    def __init__(self, analyzer_window, my_username, other_usernames, ignored_patterns):
        super().__init__()
        self.analyzer_window = analyzer_window
        self.my_username = my_username
        self.other_usernames = other_usernames
        self.ignored_patterns = ignored_patterns
        self.log_file = None

    def start_capture(self):
        logging.info("System: Capture initiated")
        self.capture_thread = CaptureThread(self.analyzer_window, self.my_username, self.other_usernames, self.ignored_patterns)
        self.capture_thread.capture_complete.connect(self.on_capture_complete)
        self.capture_thread.start()

    @pyqtSlot(list)
    def on_capture_complete(self, processed_lines):
        logging.debug(f"Received processed lines: {processed_lines}")
        if processed_lines:
            for username, message in processed_lines:
                append_to_csv(self.log_file, "first_conversation", username, message)
            logging.info(f"Text added to chat log. Last line: {processed_lines[-1][1]}")
        else:
            logging.warning("No processed lines received")
        
        self.capture_complete.emit(processed_lines)

    def check_for_new_messages(self, processed_lines):
        new_messages = self.get_new_messages(processed_lines)
        if new_messages:
            for username, message in new_messages:
                logging.info(f"New user message detected: {username}: {message}")
                append_to_csv(self.log_file, "user_message", username, message)
                
                if username in self.other_usernames:
                    self.new_message_detected.emit(username, message)
            
            return new_messages[-1][1]  # Return the last captured line
        else:
            logging.info("No new user messages detected.")
            return None

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

    def set_log_file(self, log_file):
        self.log_file = log_file