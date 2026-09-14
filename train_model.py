import os
import numpy as np
import joblib

from feature_extraction import extract_features


AUDIO_FOLDER = "audio"


# Store features and labels
X = []
y = []


for file in os.listdir(AUDIO_FOLDER):

    if file.endswith(".wav"):

        file_path = os.path.join(AUDIO_FOLDER, file)

        features = extract_features(file_path)

        X.append(features)

        # Label the audio
        if file.startswith("real"):
            y.append(0)
        elif file.startswith("ai"):
            y.append(1)


# Convert to NumPy arrays
X = np.array(X)
y = np.array(y)


print("\nTraining dataset created!")

print("X shape:", X.shape)
print("y shape:", y.shape)

print("\nLabels:")
print(y)