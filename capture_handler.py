import logging
from PyQt5.QtCore import QObject, pyqtSignal
from utils import append_to_csv, is_ignored_line

class CaptureHandler(QObject):
    capture_complete = pyqtSignal(list)

    def __init__(self, analyzer_window, my_username, other_usernames, ignored_patterns):
        super().__init__()
        self.analyzer_window = analyzer_window
        self.my_username = my_username
        self.other_usernames = other_usernames
        self.ignored_patterns = ignored_patterns
        self.log_file = None
        self.last_captured_text = None

    def set_log_file(self, log_file):
        self.log_file = log_file

    def reset_capture_state(self):
        self.last_captured_text = None

    def start_capture(self):
        try:
            captured_text = self.analyzer_window.capture_screen()
            processed_lines = self.process_captured_text(captured_text)
            new_text = self.get_new_text(processed_lines)

            if new_text:
                logging.info("New Text is found updating database")
                for username, message in new_text:
                    append_to_csv(self.log_file, "captured_conversation", username, message)
            else:
                logging.info("No new text found")

            self.capture_complete.emit(new_text)
            return new_text
        except Exception as e:
            logging.error(f"Error during capture: {str(e)}")
            self.capture_complete.emit([])
            return []

    def process_captured_text(self, text):
        lines = text.split('\n')
        processed_lines = []
        current_username = None

        for line in lines:
            line = line.strip()
            if not line or is_ignored_line(line, self.ignored_patterns):
                continue

            for username in [self.my_username] + self.other_usernames:
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

        return processed_lines

    def get_new_text(self, processed_lines):
        if self.last_captured_text is None:
            self.last_captured_text = processed_lines
            return processed_lines
        
        new_text = [line for line in processed_lines if line not in self.last_captured_text]
        self.last_captured_text = processed_lines
        return new_text