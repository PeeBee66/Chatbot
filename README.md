# Automatic Chat Reader/Replyer

## Overview

The **Automatic Chat Reader** is a Basic chat application designed to monitor and interact with chat conversations automatically. It uses screen capture and optical character recognition (OCR) to read chat messages, and can optionally respond to messages using the Ollama API for AI-generated responses.

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
     ```
     pip install -r requirements.txt
          

## Setup and Configuration

1. Clone or download this repository to your local machine.

2. For testing purposes you can use this basic web based chat app https://github.com/PeeBee66/Chat_tester 

## How to Use

1. **Launch the Application**
   - Run `python main.py` from the command line in the project directory

![image](https://github.com/user-attachments/assets/aa28a013-4b82-4edc-a1fc-1f7c68eb6756)

2. **Configure Settings**
   - Click the "Settings" button in the main window
   - Set the correct path for ollama API and Port and Test it
   - Set the Capture Interal (reccommended min 30 sec)
   - Configure usernames (Other username can only support 1 name atm)
   - Set the Background Promt
   - Set the Ignored Lines
   - Save the settings
   - Set the X and Y settings

![image](https://github.com/user-attachments/assets/66511ee2-e3ec-4aa0-8727-52313e54a45c)

3. **Initiate Capture**
   - Click the "Capture" button to start the initial screen capture
   - A transparent window will appear - position this over your chat window

![image](https://github.com/user-attachments/assets/b97ed761-f4b6-4cf3-9467-bb4aaa16127a)

4. **Start Automatic Reading**
   - Click the "Start" button to begin continuous monitoring
   - The application will now periodically capture and process chat messages

5. **Monitor Activity**
   - The main window will display captured messages and any AI responses
   - Check the "Last Captured Line" field to ensure proper capture
   - Check the logs/chatlog000X.csv for more info
   - Check the debug_screenshot.png

6. **Stop\Restart Reading**
   - Click the "Stop" button to halt the automatic reading process if needed
   - Click the capture button to restart the reading with a new CVS

7. **AI Responses (Optional)**
   - The application will automatically generate and type responses using the Ollama API
   - If using the testing web chat make sure you select the correct username for the ollama reply (should be my Username)

## Troubleshooting

- If text is not being captured correctly, try adjusting the size and position of the transparent capture window
- Ensure Tesseract OCR is correctly installed and the path is properly set in the settings
- Check that the Ollama Docker container is running if using AI responses

## Known Issues

- The application may occasionally fail to recognize changes in the chat. We are working on a fix for this issue.

## Contributing

We welcome contributions to improve the Automatic Chat Reader. Please feel free to submit issues or pull requests on our GitHub repository.
