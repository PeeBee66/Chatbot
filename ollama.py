import requests
import json

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
            "stream": False  # Changed to False for simplicity
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            json_response = response.json()
            return json_response.get('response', '')
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"