import sounddevice as sd

def record_audio(duration, sample_rate):
    sd.default.device=None
    audio = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype='float32')
    sd.wait()
    return audio.flatten()