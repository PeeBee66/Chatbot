import requests
import json

# Ollama API base URL
base_url = "http://172.21.32.180:11434"

# Function to generate a response
def generate_response(prompt, model="llama3.1:latest", context=None):
    url = f"{base_url}/api/generate"
    system_prompt = "You are a helpful assistant. Keep your responses concise, using no more than 2 sentences."
    full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
    
    data = {
        "model": model,
        "prompt": full_prompt,
        "stream": True
    }
    if context:
        data["context"] = context
    
    response = requests.post(url, json=data, stream=True)
    full_response = ""
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            if 'response' in json_response:
                full_response += json_response['response']
                print(json_response['response'], end='', flush=True)
            if json_response.get('done', False):
                context = json_response.get('context', None)
                break
    print()  # New line after response
    return full_response, context

def main():
    print("Ollama Conversation Bot (Concise Mode)")
    print("Type 'exit' to end the conversation.")
    
    context = None
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        print("\nOllama:", end=' ')
        _, context = generate_response(user_input, context=context)

if __name__ == "__main__":
    main()