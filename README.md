# Live Stream Subtitle and Translation System

This is a Python-based prototype application that records audio chunks from a microphone, passes them to a Voice Activity Detection (VAD) model, transcribes the speech using a local Whisper model, and translates the text using a free Google Translate web endpoint scraper. 

The system implements a sequential, blocking loop, meaning it is not a true asynchronous continuous stream.

## Architecture and Limitations

### 1. Audio Capture (Sequential Chunking)
- **Mechanism:** The system uses `sounddevice.rec` in a blocking manner to record audio in 1.2-second chunks (configured in `utils/config.py`). 
- **Limitation:** Because recording and transcription occur sequentially in the same thread, the microphone is completely deaf to new audio while the Whisper model is processing the previous chunk. 

### 2. Voice Activity Detection (VAD)
- **Mechanism:** Each 1.2-second chunk is converted to a PyTorch tensor and analyzed by the `silero-vad` model. If no speech is detected, the audio array is discarded.
- **Limitation:** The VAD analysis adds overhead to the blocking loop.

### 3. Speech-to-Text (Whisper)
- **Mechanism:** The application loads the `small` Whisper model locally.
- **Processing Logic:** 
  - **Partial output:** If 2 or more chunks are accumulated and the chunk count is even, the buffer is transcribed with `beam_size=3`.
  - **Final output:** If 1 silent chunk is detected, or the buffer reaches `MAX_CHUNKS` (default 3, approx 3.6 seconds), it processes the buffer with `beam_size=5` and `best_of=5`, treats it as a final phrase, and clears the buffer.

### 4. Text Processing
- The text processing pipeline consists of basic string manipulations and library calls applied only to the final output:
  - Capitalizes the first letter and appends a `.` if missing.
  - Hard-replaces `" and"` with `".And"` and `" but"` with `".But"` to force sentence splits.
  - Uses `TextBlob` for synchronous grammar and spelling correction (only if the sentence has > 3 words).
  - Removes identical adjacent words.

### 5. Translation
- **Mechanism:** Relies on the `deep-translator` package, which acts as a web client to scrape Google Translate's free public endpoint. 
- **Limitation:** This is a synchronous network call that blocks the main loop. It is susceptible to rate-limiting and requires an active internet connection.

### 6. User Interfaces
The system provides two rudimentary interfaces:
1. **CLI (`main.py`)**: A simple console script that loops infinitely until `Ctrl+C` is pressed.
2. **Streamlit UI (`ui/streamlit_app.py`)**: A web interface that spawns the blocking `while True` loop inside a detached Python `threading.Thread`. 
   - **Known Issue:** The Streamlit app currently passes 3 arguments to the `translate_text` function, whereas the function is defined to accept only 2. This will result in a `TypeError` crash at runtime when speech is finalized. Additionally, clicking "Start" multiple times will spawn overlapping concurrent threads that contend for the microphone.

---

## Directory Structure
- `audio/detector.py`: Unused volume-based fallback detector.
- `audio/recorder.py`: Blocking `sounddevice` implementation.
- `audio/silero_vad.py`: PyTorch hub Silero VAD implementation.
- `models/whisper_model.py`: Hardcoded `small` Whisper model loader.
- `processing/grammar.py`: `TextBlob` wrapper.
- `processing/text_cleaner.py`: String manipulation logic.
- `processing/translator.py`: `deep-translator` Google Translate wrapper.
- `ui/streamlit_app.py`: Streamlit frontend with threading.
- `utils/config.py`: Hardcoded configuration variables.
- `main.py`: Command-line loop.

---

## Setup Instructions

1. **Prerequisites**: Python 3.8+, FFmpeg installed on system PATH, and a working microphone.
2. **Install requirements**:
   ```bash
   pip install sounddevice numpy torch openai-whisper textblob deep-translator streamlit
   ```
3. **Initialize external models**:
   ```bash
   python -m textblob.download_corpora
   ```
4. **Run**:
   - CLI: `python main.py`
   - UI: `streamlit run ui/streamlit_app.py` 
