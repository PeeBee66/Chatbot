from PyQt5.QtCore import QThread, pyqtSignal
from utils import process_captured_text
import logging

class CaptureThread(QThread):
    capture_complete = pyqtSignal(list)

    def __init__(self, analyzer_window, my_username, other_usernames, ignored_patterns):
        super().__init__()
        self.analyzer_window = analyzer_window
        self.my_username = my_username
        self.other_usernames = other_usernames
        self.ignored_patterns = ignored_patterns

    def run(self):
        logging.debug("CaptureThread started")
        text = self.analyzer_window.capture_screen()
        logging.debug(f"Raw captured text: {text[:100]}...")  # Log first 100 characters
        processed_lines = process_captured_text(text, self.my_username, self.other_usernames, self.ignored_patterns)
        logging.debug(f"Processed lines: {processed_lines}")
        self.capture_complete.emit(processed_lines)