import requests
import logging
import time
from requests.exceptions import RequestException, Timeout, ConnectionError

class OllamaAPI:
    def __init__(self, base_url, model):
        self.base_url = base_url
        self.model = model
        self.max_retries = 3
        self.timeout = 120  # Increased timeout to 60 seconds

    def send_request(self, system_prompt, instruction, text):
        url = f"{self.base_url}/api/generate"
        full_prompt = f"{system_prompt}\n\n{instruction}\n\nHuman: {text}\n\nAssistant:"
        
        data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=data, timeout=self.timeout)
                response.raise_for_status()
                json_response = response.json()
                logging.info(f"Ollama API response received for prompt: {text[:50]}...")
                return json_response.get('response', '')
            except Timeout:
                logging.warning(f"Attempt {attempt + 1} timed out. Retrying...")
            except ConnectionError:
                logging.warning(f"Attempt {attempt + 1} failed due to connection error. Retrying...")
            except RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
            
            time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Failed to get response from Ollama API after {self.max_retries} attempts")