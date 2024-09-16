import time
import logging
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
import pyautogui

class OllamaResponseHandler(QDialog):
    def __init__(self, parent, ollama_api, system_prompt, user_prompt, user_message, chat_input_position):
        super().__init__(parent)
        self.ollama_api = ollama_api
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.user_message = user_message
        self.chat_input_position = chat_input_position
        self.response = None
        self.error = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Response")
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()

        self.status_label = QLabel("Replying with AI...", self)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def process_response(self):
        self.show()
        QTimer.singleShot(100, self._process)

    def _process(self):
        try:
            self.status_label.setText("Sending chat to AI...")
            for attempt in range(self.ollama_api.max_retries):
                try:
                    self.response = self.ollama_api.send_request(self.system_prompt, self.user_prompt, self.user_message)
                    break
                except Exception as e:
                    if attempt < self.ollama_api.max_retries - 1:
                        self.status_label.setText(f"Retry attempt {attempt + 1}...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise

            if not self.response:
                raise Exception("Failed to get response from Ollama after multiple attempts")

            self.status_label.setText("Reply generated")
            time.sleep(1)

            self.status_label.setText("Finding chat box...")
            pyautogui.click(self.chat_input_position.x, self.chat_input_position.y)
            time.sleep(1)

            self.status_label.setText("Entering chat text...")
            pyautogui.typewrite(self.response)
            time.sleep(1)

            self.status_label.setText("Submitting chat text...")
            pyautogui.press('enter')
            time.sleep(1)

        except Exception as e:
            self.error = str(e)
            self.status_label.setText(f"Error: {self.error}")
            logging.error(f"Error in Ollama response: {self.error}")
            time.sleep(3)

        finally:
            self.close()

def handle_ollama_response(parent, ollama_api, system_prompt, user_prompt, user_message, chat_input_position):
    handler = OllamaResponseHandler(parent, ollama_api, system_prompt, user_prompt, user_message, chat_input_position)
    handler.process_response()
    return handler.response, handler.error