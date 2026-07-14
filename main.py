from audio.recorder import record_audio
from audio.silero_vad import is_speaking
from models.whisper_model import load_model
from processing.text_cleaner import add_basic_punctuation, split_sentences, remove_repetition
from processing.grammar import grammar_correct
from processing.translator import translate_text, languages
from utils.config import SAMPLE_RATE, THRESHOLD, MAX_CHUNKS, DURATION, MIN_SPEECH_CHUNKS, TARGET_LANG

import numpy as np
import torch
import time

model = load_model()

buffer = []
silence_count = 0
partial_text = ""
last_text = ""
chunk_counter = 0

try:
    while True:


        audio= record_audio(DURATION, SAMPLE_RATE)

        volume = np.mean(np.abs(audio))

        if is_speaking(audio,SAMPLE_RATE):
            print("🟢 Speaking...")

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
                    fp16=torch.cuda.is_available(),
                    temperature=0,
                    beam_size=3,
                    best_of=3
                )
                text = result["text"].strip()

                if text != "" and text != partial_text:
                    print("⌨️", text)
                    partial_text = text

        else:
            print("🔴 Silence...")
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
                fp16=False,
                temperature=0,
                best_of=5,
                beam_size=5
            )
            text = result["text"].strip()

            if len(text.split()) < 2:
                buffer = []
                silence_count = 0
                continue

            text = add_basic_punctuation(text)
            text = split_sentences(text)

            if len(text.split()) > 3:
                text = grammar_correct(text)

            text = remove_repetition(text)

            if text != "" and text != last_text:
                translated = translate_text(text, TARGET_LANG)

                print("✅", text)
                print(f"🌍 ({languages[TARGET_LANG]})", translated)

                last_text = text

            buffer = []
            silence_count = 0
            partial_text = ""
            chunk_counter = 0

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped manually")

except Exception as e:
    print("Error:", e)

