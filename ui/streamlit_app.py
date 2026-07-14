import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
import threading
import numpy as np
import torch
import time

from audio.recorder import record_audio
from audio.silero_vad import is_speaking
from models.whisper_model import load_model
from processing.text_cleaner import add_basic_punctuation, split_sentences, remove_repetition
from processing.grammar import grammar_correct
from processing.translator import translate_text, languages
from utils.config import SAMPLE_RATE, MAX_CHUNKS, DURATION, MIN_SPEECH_CHUNKS

# Load model

model = load_model()

# UI setup

st.set_page_config(page_title="AI Subtitles", layout="centered")

st.title("🎙️ Live Multilingual Subtitles")

target_lang = st.selectbox("🌍 Select Output Language", list(languages.keys()))

status_box = st.empty()
typing_box = st.empty()
final_box = st.empty()
translation_box = st.empty()

start = st.button("▶️ Start")

    
def run_system():
    buffer = []
    silence_count = 0
    partial_text = ""
    last_text = ""
    chunk_counter = 0

    while True:
        audio = record_audio(DURATION, SAMPLE_RATE)

        if is_speaking(audio, SAMPLE_RATE):
            status_box.markdown("🟢 **Speaking...**")

            buffer.append(audio)
            silence_count = 0
            chunk_counter += 1

            if len(buffer) < MIN_SPEECH_CHUNKS:
                continue

            if chunk_counter % 2 == 0:
                full_audio = np.concatenate(buffer)

                if np.max(np.abs(full_audio)) > 0:
                    full_audio = full_audio / np.max(np.abs(full_audio))

                result = model.transcribe(
                    full_audio,
                    task="transcribe",
                    fp16=torch.cuda.is_available(),
                    temperature=0,
                    beam_size=3,
                    best_of=3
                )

                text = result["text"].strip()

                if text and text != partial_text:
                    typing_box.markdown(f"⌨️ {text}")
                    partial_text = text

        else:
            status_box.markdown("🔴 **Silence...**")
            silence_count += 1

        if (silence_count >= 1 or len(buffer) >= MAX_CHUNKS) and len(buffer) > 0:

            if len(buffer) < MIN_SPEECH_CHUNKS:
                buffer = []
                silence_count = 0
                continue

            full_audio = np.concatenate(buffer)

            if np.max(np.abs(full_audio)) > 0:
                full_audio = full_audio / np.max(np.abs(full_audio))

            result = model.transcribe(
                full_audio,
                task="transcribe",
                fp16=torch.cuda.is_available(),
                temperature=0,
                beam_size=3,
                best_of=3
            )

            text = result["text"].strip()
            detected_lang = result["language"]

            if len(text.split()) < 2:
                buffer = []
                silence_count = 0
                continue

            text = add_basic_punctuation(text)
            text = split_sentences(text)

            if len(text.split()) > 3:
                text = grammar_correct(text)

            text = remove_repetition(text)

            if text and text != last_text:
                translated = translate_text(text, detected_lang, target_lang)

                final_box.markdown(f"## ✅ {text}")
                translation_box.markdown(f"## 🌍 ({languages[target_lang]}) {translated}")

                last_text = text

            buffer = []
            silence_count = 0
            partial_text = ""
            chunk_counter = 0

        time.sleep(0.1)

if start:
    threading.Thread(target=run_system).start()
