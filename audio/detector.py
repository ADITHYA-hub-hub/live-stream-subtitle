import numpy as np

def is_speaking(audio, threshold):
    volume = np.mean(np.abs(audio))
    return volume > threshold