import logging
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt
from utils import append_to_csv

class OllamaWorker(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, ollama_api, system_prompt, username, message, chat_input_position, conversation_history):
        super().__init__()
        self.ollama_api = ollama_api
        self.system_prompt = system_prompt
        self.username = username
        self.message = message
        self.chat_input_position = chat_input_position
        self.conversation_history = conversation_history

    def run(self):
        try:
            # Prepare the prompt with the conversation history
            full_prompt = self.system_prompt + "\n\nConversation history:\n"
            for user, msg in self.conversation_history:
                full_prompt += f"{user}: {msg}\n"
            full_prompt += f"\nPlease respond to the following message from {self.username}:"

            response = self.ollama_api.send_request(full_prompt, f"Message from {self.username}:", self.message)
            self.finished.emit(response, "")
        except Exception as e:
            self.finished.emit("", str(e))

class AIHandler(QObject):
    response_ready = pyqtSignal(str, str)
    ai_response_complete = pyqtSignal()

    def __init__(self, ollama_api, background_prompt, chat_position_handler):
        super().__init__()
        self.ollama_api = ollama_api
        self.background_prompt = background_prompt
        self.chat_position_handler = chat_position_handler
        self.log_file = None

    def set_log_file(self, log_file):
        self.log_file = log_file

    def process_new_message(self, username, message, chat_input_position, conversation_history):
        # Create and show progress dialog
        progress = QProgressDialog("Processing message...", "Cancel", 0, 0)
        progress.setWindowTitle("AI Response")
        progress.setWindowFlags(progress.windowFlags() | Qt.WindowStaysOnTopHint)
        progress.setModal(True)
        progress.show()

        # Create worker thread
        self.worker = OllamaWorker(self.ollama_api, self.background_prompt, username, message, chat_input_position, conversation_history)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(progress.close)
        self.worker.start()

    def on_worker_finished(self, response, error):
        if error:
            logging.error(f"Error in Ollama response: {error}")
        else:
            logging.info(f"Ollama's response: {response}")
            # Type the response into the chat
            self.chat_position_handler.type_message(response)
            # Update the CSV with Ollama's response
            if self.log_file:
                append_to_csv(self.log_file, "ollama_auto_reply", "Ollama", response)
                logging.info(f"Reply sent to $Other user from Ollama.")
            else:
                logging.warning("Log file not set, unable to append Ollama response to CSV")
        self.response_ready.emit(response, error)
        self.ai_response_complete.emit()

    def set_background_prompt(self, prompt):
        self.background_prompt = prompt