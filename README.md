# Live Stream Subtitle and Translation System

This application captures live audio from a microphone, detects when speech is occurring, transcribes the speech into text using a local speech recognition model, post-processes the text for spelling and readability, and translates the output into a chosen target language in real-time.

The system provides two interfaces:
1. A terminal-based interface for command-line execution.
2. A web-based interface using Streamlit for a graphical user experience.

---

## Features

- **Real-Time Audio Recording**: Captures audio input in continuous segments from the default recording device.
- **Voice Activity Detection (VAD)**: Utilizes a neural network model to determine if human speech is present in the recorded segment, discarding silent segments to save computing resources.
- **Speech-to-Text Transcription**: Transcribes the captured audio buffer into text using the Whisper model.
- **Text Post-Processing**:
  - Capitalization and automatic sentence-boundary punctuation.
  - Sentence splitting on conjunctions like "and" or "but" for readable subtitle formatting.
  - Word repetition removal to eliminate stutters or duplicated outputs.
  - Basic spelling and grammar correction using TextBlob.
- **Multilingual Translation**: Translates text into target languages including English, Tamil, Hindi, Telugu, Korean, and Japanese.

---

## System Architecture

The data pipeline runs through the following sequence:

```
[ Audio Input Device ]
          │ (1.2-second chunks)
          ▼
[ Voice Activity Detection ] ──(Silence detected)──► [ Discard Segment ]
          │ (Speech detected)
          ▼
[ Accumulating Buffer ]
          │ (Buffer size threshold met or silence begins)
          ▼
[ Speech-to-Text Engine ] ◄── Uses Whisper model
          │ (Raw Transcription)
          ▼
[ Text Cleaner & Grammar Correction ] ◄── Capitalizes, punctuates, corrects spelling
          │ (Cleaned Transcription)
          ▼
[ Translation Engine ] ◄── Translates via Google Translate (free web interface)
          │ (Translated Text)
          ▼
[ Display Output ] (Terminal / Streamlit Web App)
```

---

## Directory Structure

- [audio/](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/audio)
  - [detector.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/audio/detector.py): Simple volume-based speech detector (alternative threshold method).
  - [recorder.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/audio/recorder.py): Captures raw mono float32 audio via sounddevice.
  - [silero_vad.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/audio/silero_vad.py): Speech verification using Silero VAD.
- [models/](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/models)
  - [whisper_model.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/models/whisper_model.py): Handles loading the local Whisper model (uses GPU/CUDA if available, otherwise CPU).
- [processing/](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/processing)
  - [grammar.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/processing/grammar.py): Corrects grammar and spelling using TextBlob.
  - [text_cleaner.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/processing/text_cleaner.py): Standardizes capitalization, removes immediate word repetition, and inserts punctuation.
  - [translator.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/processing/translator.py): Translates text via Google Translate (free web interface).
- [ui/](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/ui)
  - [streamlit_app.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/ui/streamlit_app.py): Implementation of the Streamlit-based web interface.
- [utils/](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/utils)
  - [config.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/utils/config.py): Project configuration settings.
  - [helpers.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/utils/helpers.py): Helper utilities.
- [main.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/main.py): Entry point for the command-line application.
- [requirements.txt](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/requirements.txt): List of Python library dependencies.

---

## Prerequisites

1. **Python**: Version 3.8, 3.9, 3.10, or 3.11 is required.
2. **FFmpeg**: Required by Whisper for audio file operations.
   - **Windows**: Install using PowerShell: `winget install Gyan.FFmpeg`
   - **macOS**: Install using Homebrew: `brew install ffmpeg`
   - **Linux**: Install via package manager: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora).
3. **Audio Input**: A functioning microphone connected to the system.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ADITHYA-hub-hub/live-stream-subtitle.git
   cd live-stream-subtitle
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   ```
   Activate the virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download TextBlob Corpora**:
   TextBlob requires specific linguistic databases to perform grammar corrections. Download them by running:
   ```bash
   python -m textblob.download_corpora
   ```

---

## Usage

### Command-Line Interface
To run the system in your terminal:
```bash
python main.py
```
This script will:
1. Load the speech recognition model on your system.
2. Monitor input from the microphone.
3. Output the transcription and translation directly to the console.
4. Press `Ctrl + C` in the terminal to stop execution.

### Web Interface
To run the browser-based dashboard:
```bash
streamlit run ui/streamlit_app.py
```
Inside the web app:
1. Select your desired output language from the dropdown menu.
2. Click the **Start** button to begin recording.
3. View active speech status, live partial transcriptions, final subtitles, and translation outputs in real-time.

---

## Configuration

Adjust settings inside [utils/config.py](file:///c:/Projects/AI-based%20live%20stream%20subtitle%20and%20translation%20system/utils/config.py) to tune behavior:

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `SAMPLE_RATE` | `16000` | Audio sampling frequency in Hz (Whisper requires 16000). |
| `DURATION` | `1.2` | Length of each recorded audio chunk in seconds. |
| `MIN_SPEECH_CHUNKS` | `2` | Minimum speech chunks to accumulate before starting real-time transcription. |
| `MAX_CHUNKS` | `3` | Maximum number of chunks to accumulate before forcing transcription. |
| `TARGET_LANG` | `"ko"` | Default language code for translation outputs. |
