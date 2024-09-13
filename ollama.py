import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OllamaAPI:
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model

    def send_request(self, system_prompt, instruction, text):
        url = f"{self.base_url}/api/generate"
        full_prompt = f"{system_prompt}\n\n{instruction}\n\nHuman: {text}\n\nAssistant:"
        
        data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            json_response = response.json()
            logging.info(f"Ollama API response received for prompt: {text[:50]}...")
            return json_response.get('response', '')
        except requests.exceptions.ConnectionError:
            error_msg = f"Failed to connect to Ollama server at {self.base_url}. Please check if the server is running and the URL is correct."
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except requests.exceptions.Timeout:
            error_msg = f"Request to Ollama server timed out. The server at {self.base_url} is not responding in a timely manner."
            logging.error(error_msg)
            raise TimeoutError(error_msg)
        except requests.exceptions.HTTPError as http_err:
            error_msg = f"HTTP error occurred: {http_err}. Please check your Ollama server configuration."
            logging.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"An unexpected error occurred while communicating with Ollama: {str(e)}"
            logging.error(error_msg)
            raise