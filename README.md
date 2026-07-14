# AI-Based Live Stream Subtitle and Translation System

This project is a real-time, AI-powered system that captures live audio from your microphone, transcribes the speech into text, and translates it into multiple languages. It is designed to be simple and easy to run locally.

## Features

- **Live Speech-to-Text**: Uses the local **Whisper** model to accurately transcribe spoken language.
- **Voice Activity Detection (VAD)**: Uses **Silero VAD** to detect when you are speaking and ignore silence, saving processing power.
- **Text Cleaning & Grammar Correction**: Automatically capitalizes text, adds basic punctuation, removes repeated words, and fixes minor grammar mistakes using `TextBlob`.
- **Live Translation**: Translates your speech into multiple languages (Tamil, Hindi, Telugu, Korean, Japanese) using Google Translate via the `deep-translator` library.
- **Web Interface (Streamlit)**: A user-friendly web application to select your microphone, choose the translation language, and view live transcriptions.
- **Command-Line Interface (CLI)**: A simple console-based version for terminal users.

## Project Structure

- `main.py` - The command-line version of the application.
- `ui/streamlit_app.py` - The Streamlit web interface.
- `audio/` - Handles microphone recording and voice activity detection (VAD).
- `models/` - Loads the Whisper speech-to-text model.
- `processing/` - Handles text cleaning, grammar correction, and translation.
- `utils/config.py` - Contains system configurations like sample rate and chunk duration.

## How It Works

1. **Audio Recording**: The system records audio in small chunks (1.2 seconds).
2. **VAD Check**: It analyzes the chunk to see if it contains speech. If it's just silence, it is ignored.
3. **Transcription**: If speech is detected, the audio is sent to the Whisper model which converts the audio into text.
4. **Text Processing**: The text is cleaned up and grammar-corrected.
5. **Translation**: The final text is translated into the selected target language.
6. **Output**: The transcription and translation are displayed on the screen!

## Setup and Installation

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- A working microphone.
- **FFmpeg** installed and added to your system PATH (required by Whisper).

### 2. Install Dependencies
Open your terminal and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Initialize TextBlob Corpora
Download the necessary files for grammar correction:

```bash
python -m textblob.download_corpora
```

## Running the Application

You can run the system in two ways:

### Option 1: Web Interface (Recommended)
Launch the Streamlit web application:
```bash
streamlit run ui/streamlit_app.py
```
This will open an interactive web interface in your browser where you can start/stop the system and change settings easily.

### Option 2: Command-Line Interface (CLI)
If you prefer the terminal, you can run the basic script:
```bash
python main.py
```
Press `Ctrl+C` to stop the script.
