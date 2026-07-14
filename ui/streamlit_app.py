import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import numpy as np
import torch
import sounddevice as sd

from audio.recorder import record_audio
from audio.silero_vad import is_speaking
from models.whisper_model import load_model
from processing.text_cleaner import add_basic_punctuation, split_sentences, remove_repetition
from processing.grammar import grammar_correct
from processing.translator import translate_text, languages
from utils.config import SAMPLE_RATE, MAX_CHUNKS, DURATION, MIN_SPEECH_CHUNKS

# Load model (Cached to prevent reloading on every UI click)
@st.cache_resource
def get_model():
    return load_model()

model = get_model()

# UI setup
st.set_page_config(page_title="AI Subtitles", layout="centered")
st.title("🎙️ Live Multilingual Subtitles")

# Microphone selection
try:
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    input_devices = {}
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            api_name = hostapis[d['hostapi']]['name']
            input_devices[i] = f"{d['name']} [{api_name}]"
except Exception as e:
    input_devices = {None: "Default Microphone"}

if input_devices:
    selected_mic_name = st.selectbox("🎙️ Select Microphone", list(input_devices.values()))
    selected_mic_idx = [i for i, name in input_devices.items() if name == selected_mic_name][0]
else:
    st.error("No microphones detected on this system!")
    selected_mic_idx = None

# Output language selection
lang_names = [name.capitalize() for name in languages.values()]
target_lang_name = st.selectbox("🌍 Select Output Language", lang_names)
target_lang = [k for k, v in languages.items() if v.capitalize() == target_lang_name][0]

# Control Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start", use_container_width=True):
        st.session_state.running = True
with col2:
    if st.button("⏹️ Stop", use_container_width=True):
        st.session_state.running = False

# Initialize session state for the persistent buffer and history
if 'buffer' not in st.session_state:
    st.session_state.buffer = []
    st.session_state.silence_count = 0
    st.session_state.partial_text = ""
    st.session_state.last_text = ""
    st.session_state.chunk_counter = 0
    st.session_state.translation_history = ""
    st.session_state.status_msg = "🟢 **Starting...**"

# The main active processing block (Replaces background threading)
if st.session_state.get('running', False):
    
    # 1. Draw the UI *before* we block the thread waiting for audio
    st.markdown(st.session_state.get('status_msg', "🟢 **Starting...**"))
    
    if st.session_state.partial_text:
        st.markdown(f"⌨️ {st.session_state.partial_text}")
        
    if st.session_state.translation_history:
        st.markdown(st.session_state.translation_history)

    try:
        # 2. Record one chunk of audio from the selected device (BLOCKS for 1.2s)
        audio = record_audio(DURATION, SAMPLE_RATE, device=selected_mic_idx)
        vol = np.max(np.abs(audio)) if len(audio) > 0 else 0.0
        
        if is_speaking(audio, SAMPLE_RATE):
            st.session_state.status_msg = f"🟢 **Speaking...** (Vol: {vol:.4f})"
            st.session_state.buffer.append(audio)
            st.session_state.silence_count = 0
            st.session_state.chunk_counter += 1

            # Partial typing transcription
            if len(st.session_state.buffer) >= 1:
                full_audio = np.concatenate(st.session_state.buffer)
                if np.max(np.abs(full_audio)) > 0:
                    full_audio = full_audio / np.max(np.abs(full_audio))

                result = model.transcribe(
                    full_audio,
                    task="transcribe",
                    fp16=False,
                    temperature=0,
                    beam_size=3,
                    best_of=3
                )
                text = result["text"].strip()
                print(f"DEBUG (Partial): '{text}'")
                if text and text != st.session_state.partial_text:
                    st.session_state.partial_text = text
        else:
            st.session_state.status_msg = f"🔴 **Silence...** (Vol: {vol:.4f})"
            st.session_state.silence_count += 1

        # Finalize sentence when silence is detected or buffer is maxed
        if (st.session_state.silence_count >= 1 or len(st.session_state.buffer) >= MAX_CHUNKS) and len(st.session_state.buffer) > 0:
            full_audio = np.concatenate(st.session_state.buffer)
            if np.max(np.abs(full_audio)) > 0:
                full_audio = full_audio / np.max(np.abs(full_audio))

            result = model.transcribe(
                full_audio,
                task="transcribe",
                fp16=False,
                temperature=0,
                beam_size=3,
                best_of=3
            )

            text = result["text"].strip()
            detected_lang = result.get("language", "en")
            print(f"DEBUG (Final) [{detected_lang}]: '{text}'")

            if len(text.strip()) > 0:
                text = add_basic_punctuation(text)
                text = split_sentences(text)
                
                # Only apply English grammar correction if the spoken language is actually English!
                if len(text.split()) > 3 and detected_lang == "en":
                    text = grammar_correct(text)
                    
                text = remove_repetition(text)

                if text and text != st.session_state.last_text:
                    translated = translate_text(text, target_lang)
                    
                    # Add to scrolling history
                    new_entry = f"**✅ {text}**\n\n*🌍 ({languages[target_lang].capitalize()}) {translated}*\n\n---\n\n"
                    st.session_state.translation_history = new_entry + st.session_state.translation_history
                    st.session_state.last_text = text

            # Reset states for the next sentence
            st.session_state.buffer = []
            st.session_state.silence_count = 0
            st.session_state.partial_text = ""
            st.session_state.chunk_counter = 0

        # Trigger rapid restart of the script loop to grab the next chunk of audio
        st.rerun()

    except Exception as e:
        st.error(f"Error reading from microphone: {str(e)}")
        st.session_state.running = False
else:
    st.markdown("⏸️ **Ready. Click Start.**")
