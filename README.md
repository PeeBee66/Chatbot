# Automatic Chat Reader

## Overview

The **Automatic Chat Reader** is a sophisticated application designed to monitor and interact with chat conversations automatically. It uses screen capture and optical character recognition (OCR) to read chat messages, and can optionally respond to messages using the Ollama API for AI-generated responses.

## Features

- Automatic chat message capture and processing
- AI-powered responses using Ollama API
- Customizable settings for ignored users and specific chats
- Ability to ignore replied-to messages
- User-friendly interface for easy operation and monitoring

## Prerequisites

Before you can run the Automatic Chat Reader, you need to install the following:

1. **Tesseract OCR**
   - Download and install Tesseract for Windows from the [official GitHub repository](https://github.com/UB-Mannheim/tesseract/wiki)
   - Make note of the installation path (default is usually `C:\Program Files\Tesseract-OCR`)

2. **Ollama Docker**
   - Install Docker on your system if you haven't already
   - Pull and run the Ollama Docker image by following instructions on the [Ollama Docker GitHub page](https://github.com/jmorganca/ollama)

3. **Python Dependencies**
   - Install required Python packages by running:
     ```bash
     pip install PyQt5 pillow pytesseract pyautogui
     ```

## Setup and Configuration

1. Clone or download this repository to your local machine.

2. Open `settings.py` and update the following:
   - Set the correct path for Tesseract OCR
   - Configure the Ollama API URL (default is usually correct if running locally)

3. Adjust any other settings in `settings.json` as needed (e.g., capture interval, usernames to ignore)

## How to Use

1. **Launch the Application**
   - Run `python main.py` from the command line in the project directory

2. **Configure Settings**
   - Click the "Settings" button in the main window
   - Set your username and other usernames to monitor
   - Adjust the capture interval and other parameters as needed
   - Click "Save" to apply the settings

3. **Initiate Capture**
   - Click the "Capture" button to start the initial screen capture
   - A transparent window will appear - position this over your chat window

4. **Start Automatic Reading**
   - Click the "Start" button to begin continuous monitoring
   - The application will now periodically capture and process chat messages

5. **Monitor Activity**
   - The main window will display captured messages and any AI responses
   - Check the "Last Captured Line" field to ensure proper capture

6. **Stop Reading**
   - Click the "Stop" button to halt the automatic reading process

7. **AI Responses (Optional)**
   - If enabled, the application will automatically generate and type responses using the Ollama API

## Troubleshooting

- If text is not being captured correctly, try adjusting the size and position of the transparent capture window
- Ensure Tesseract OCR is correctly installed and the path is properly set in the settings
- Check that the Ollama Docker container is running if using AI responses

## Known Issues

- The application may occasionally fail to recognize changes in the chat. We are working on a fix for this issue.

## Contributing

We welcome contributions to improve the Automatic Chat Reader. Please feel free to submit issues or pull requests on our GitHub repository.
