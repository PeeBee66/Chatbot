import logging
import csv
from ollama_handler import handle_ollama_response

class AIHandler:
    def __init__(self, ollama_api, background_prompt):
        self.ollama_api = ollama_api
        self.background_prompt = background_prompt

    def process_new_message(self, log_file, username, message, chat_input_position):
        # Get all messages from the CSV
        with open(log_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            all_messages = list(reader)

        # Construct the conversation history
        conversation_history = [f"{row[2]}: {row[3]}" for row in all_messages]
        
        # Construct the system prompt
        system_prompt = f"{self.background_prompt}\n\nCurrent chat:\n" + "\n".join(conversation_history)

        # Get the last messages from the triggering user
        user_messages = [msg for msg in reversed(all_messages) if msg[2] == username]
        last_user_conversation = "\n".join([f"{msg[2]}: {msg[3]}" for msg in user_messages])

        # Use the OllamaResponseHandler
        response, error = handle_ollama_response(
            None,  # We don't need the parent widget here
            self.ollama_api,
            system_prompt,
            f"Please respond to the following conversation from {username}:",
            last_user_conversation,
            chat_input_position
        )

        if error:
            logging.error(f"Error in Ollama response: {error}")
            return None, error
        else:
            logging.info(f"Ollama's response: {response}")
            return response, None

    def set_background_prompt(self, prompt):
        self.background_prompt = prompt