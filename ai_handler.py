import logging
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QProgressDialog
from ollama_handler import handle_ollama_response

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
        # Prepare the prompt with the conversation history
        full_prompt = self.system_prompt + "\n\nConversation history:\n"
        for user, msg in self.conversation_history:
            full_prompt += f"{user}: {msg}\n"
        full_prompt += f"\nPlease respond to the following message from {self.username}:"

        response, error = handle_ollama_response(
            None,  # We don't need the parent widget here
            self.ollama_api,
            full_prompt,
            f"Message from {self.username}:",
            self.message,
            self.chat_input_position
        )
        self.finished.emit(response, error)

class AIHandler(QObject):
    response_ready = pyqtSignal(str, str)

    def __init__(self, ollama_api, background_prompt):
        super().__init__()
        self.ollama_api = ollama_api
        self.background_prompt = background_prompt

    def process_new_message(self, log_file, username, message, chat_input_position, conversation_history):
        # Create and show progress dialog
        progress = QProgressDialog("Processing message...", "Cancel", 0, 0)
        progress.setWindowTitle("AI Response")
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
        self.response_ready.emit(response, error)

    def set_background_prompt(self, prompt):
        self.background_prompt = prompt