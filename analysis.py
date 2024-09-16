from PyQt5.QtCore import QThread, pyqtSignal
from ollama import OllamaAPI
import csv
import logging

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

def process_new_message(message, background_prompt, ollama_api):
    try:
        logging.info("Contacting Ollama server: Please wait for response (this may take a bit depending on AI assistant speeds)")
        response = ollama_api.send_request(background_prompt, 
                                           "Please respond to the following message:", 
                                           message)
        logging.info("Received response from Ollama server")
        return response
    except Exception as e:
        logging.error(f"Error processing new message: {str(e)}")
        return ""

def get_chat_history(log_file):
    try:
        with open(log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            return [f"{row[1]}: {row[2]}" for row in reader]
    except Exception as e:
        logging.error(f"Error reading chat history: {str(e)}")
        return []

def analyze_conversation(chat_history, background_prompt, ollama_api):
    chat_history_text = "\n".join(chat_history)
    prompt = f"{background_prompt}\n\n{chat_history_text}"
    try:
        response = ollama_api.send_request(background_prompt, 
                                           "Please analyze the following conversation:", 
                                           chat_history_text)
        return response
    except Exception as e:
        logging.error(f"Error analyzing conversation: {str(e)}")
        return ""