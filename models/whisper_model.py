import whisper
import torch

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    model = whisper.load_model("small", device=device)
    return model