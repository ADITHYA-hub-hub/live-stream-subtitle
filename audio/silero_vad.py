import torch

# Load Silero VAD model
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)

(get_speech_timestamps, _, _, _, _) = utils

def is_speaking(audio, sample_rate):
    audio_tensor = torch.from_numpy(audio)

    speech = get_speech_timestamps(
        audio_tensor,
        model,
        sampling_rate=sample_rate
    )

    return len(speech) > 0