import soundfile as sf
import numpy as np
from scipy.signal import resample_poly
from math import gcd


def preprocess_audio(file_path):

    # Load WAV file
    audio, sample_rate = sf.read(
        file_path,
        dtype="float32",
        always_2d=True
    )

    print("Original sample rate:", sample_rate)
    print("Original shape:", audio.shape)

    # Convert stereo -> mono
    audio = audio.mean(axis=1)

    # Convert to 16 kHz
    if sample_rate != 16000:

        g = gcd(sample_rate, 16000)

        up = 16000 // g
        down = sample_rate // g

        audio = resample_poly(
            audio,
            up,
            down
        ).astype(np.float32)

        sample_rate = 16000

    print("Final sample rate:", sample_rate)
    print("Final samples:", len(audio))

    return audio, sample_rate

if __name__ == "__main__":
    audio, sample_rate = preprocess_audio("audio/real1.wav")
    print("\nAudio preprocessing successful!")
    print("Sample rate:", sample_rate)
    print("Audio shape:", audio.shape)
    print("Data type:", audio.dtype)