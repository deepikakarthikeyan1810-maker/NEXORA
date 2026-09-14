import librosa
import numpy as np
import os

from preprocess import preprocess_audio

AUDIO_FOLDER = "audio"


def extract_features(file_path):

    # Step 1: Preprocess audio
    audio, sample_rate = preprocess_audio(file_path)

    # Step 2: MFCC
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sample_rate,
        n_mfcc=40
    )

    # Mean of 40 MFCC features
    mfcc_features = np.mean(mfcc, axis=1)

    # Step 3: Spectral Centroid
    spectral_centroid = librosa.feature.spectral_centroid(
        y=audio,
        sr=sample_rate
    )

    # Step 4: Spectral Bandwidth
    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=audio,
        sr=sample_rate
    )

    # Step 5: Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=audio,
        sr=sample_rate
    )

    # Step 6: Zero Crossing Rate
    zero_crossing = librosa.feature.zero_crossing_rate(audio)

    # Take mean values
    spectral_centroid = np.mean(spectral_centroid)
    spectral_bandwidth = np.mean(spectral_bandwidth)
    spectral_rolloff = np.mean(spectral_rolloff)
    zero_crossing = np.mean(zero_crossing)

    # Combine all features
    features = np.concatenate([
        mfcc_features,
        [spectral_centroid],
        [spectral_bandwidth],
        [spectral_rolloff],
        [zero_crossing]
    ])

    return features


# Test all audio files

for file in os.listdir(AUDIO_FOLDER):

    if file.endswith(".wav"):

        file_path = os.path.join(AUDIO_FOLDER, file)

        features = extract_features(file_path)

        print("\nFile:", file)
        print("Total features:", len(features))
        print("First 5 values:", features[:5])