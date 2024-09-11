# Automatic Chat Reader

This project is an automatic chat reader designed to process text from chats and potentially respond to messages based on certain settings.

## Features
- Reads chat messages automatically.
- Integrates Ollama API for replying to messages.
- Ignores replied-to messages.
- Settings to ignore specific users or specific chats.

## Prerequisites
1. **Tesseract**  
   Download the Tesseract installer for Windows from the official GitHub repository:  
   [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   
2. **Ollama Docker**  
   Install Ollama API via Docker:  
   [Ollama Docker GitHub](https://github.com/valiantlynx/ollama-docker)

## To-Do
- [ ] **Integrate Ollama API** to reply to messages while ignoring already replied ones.
- [ ] Add settings to ignore specific chats.
- [ ] Add settings to ignore specific users.

## Text Size Examples

### Header (Markdown)  
This is a normal header using `###`.

<p><span style="font-size:18px">This text is 18px using HTML inline styling.</span></p>

<p><span style="font-size:24px">This text is 24px using HTML inline styling.</span></p>
