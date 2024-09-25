import logging
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from utils import create_new_log_file, append_to_csv, get_last_messages

class StartAnalyzer(QObject):
    analysis_complete = pyqtSignal(list, bool)
    ollama_response_ready = pyqtSignal(str, str)
    capture_complete = pyqtSignal(bool)

    def __init__(self, analyzer_window, capture_handler, ai_handler, chat_position_handler, capture_interval):
        super().__init__()
        self.analyzer_window = analyzer_window
        self.capture_handler = capture_handler
        self.ai_handler = ai_handler
        self.chat_position_handler = chat_position_handler
        self.capture_interval = capture_interval
        self.is_analyzing = False
        self.waiting_for_ollama = False
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.perform_capture)
        self.log_file = None
        self.ai_handler.ai_response_complete.connect(self.restart_capture)

    def capture_restart(self):
        try:
            # Stop any ongoing analysis
            self.stop_analysis()

            # Create a new CSV file and set it as the current database
            self.log_file = create_new_log_file()
            logging.info(f"New CSV file created: {self.log_file}")
            self.capture_handler.set_log_file(self.log_file)

            # Perform the capture
            captured_text = self.analyzer_window.capture_screen()
            processed_lines = self.capture_handler.process_captured_text(captured_text)

            # Add captured text to CSV
            for username, message in processed_lines:
                append_to_csv(self.log_file, "captured_conversation", username, message)

            logging.info("Initial capture completed and added to CSV")
            self.capture_complete.emit(True)
            return self.log_file
        except Exception as e:
            logging.error(f"Error during capture/restart: {str(e)}")
            self.capture_complete.emit(False)
            return None

    def start_analysis(self):
        if not self.log_file:
            raise ValueError("No capture performed. Please use Capture first.")

        self.is_analyzing = True
        logging.info(f"System: Analysis started. Will start a scan in {self.capture_interval} seconds for new Text")
        self.capture_timer.start(self.capture_interval * 1000)

    def stop_analysis(self):
        self.is_analyzing = False
        self.capture_timer.stop()
        logging.info("System: Analysis stopped")

    def perform_capture(self):
        if not self.is_analyzing or self.waiting_for_ollama:
            return

        logging.info(f"Screen Captured, {self.capture_interval} sec before next screen refresh")
        captured_text = self.analyzer_window.capture_screen()
        processed_lines = self.capture_handler.process_captured_text(captured_text)
        new_text = self.get_new_text(processed_lines)
        
        if new_text:
            self.handle_new_text(new_text)
        else:
            logging.info(f"No new text found waiting {self.capture_interval} sec to retry")

    def get_new_text(self, processed_lines):
        last_messages = get_last_messages(self.log_file, len(processed_lines))
        new_text = []
        
        for processed_line in processed_lines:
            if processed_line not in last_messages:
                new_text.append(processed_line)
        
        return new_text

    def handle_new_text(self, new_text):
        logging.info(f"New Text is found updating database. ##TEXT that was added## {new_text}")
        other_user_messages = []
        last_username = None
        for username, message in new_text:
            append_to_csv(self.log_file, "captured_conversation", username, message)
            last_username = username
            
            if username in self.capture_handler.other_usernames:
                other_user_messages.append((username, message))
            elif username == self.capture_handler.my_username:
                logging.info("User text added, no Ollama reply needed.")

        if other_user_messages and last_username in self.capture_handler.other_usernames:
            self.process_other_user_messages(other_user_messages)
        else:
            logging.info("No response needed: last message is from my username or no new messages from other users")

        self.analysis_complete.emit(new_text, self.waiting_for_ollama)

    def process_other_user_messages(self, messages):
        self.waiting_for_ollama = True
        logging.info("Contacting Ollama, not checking for new text until reply is entered.")
        self.capture_timer.stop()
        
        # Combine all messages into a single string
        combined_message = "\n".join([f"{username}: {message}" for username, message in messages])
        
        # Get the entire conversation history from the CSV
        conversation_history = get_last_messages(self.log_file, -1)  # -1 to get all messages
        
        self.ai_handler.process_new_message(messages[-1][0], combined_message, 
                                            self.chat_position_handler.get_chat_position(), 
                                            conversation_history)

    def restart_capture(self):
        self.waiting_for_ollama = False
        if self.is_analyzing:
            self.capture_timer.start(self.capture_interval * 1000)