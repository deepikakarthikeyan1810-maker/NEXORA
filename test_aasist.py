import sys
import os
import torch
import numpy as np

sys.path.append("aasist")

from AASIST import Model
from preprocess import preprocess_audio


# -----------------------------
# AASIST configuration
# -----------------------------
model_config = {
    "nb_samp": 64600,
    "first_conv": 128,
    "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
    "gat_dims": [64, 32],
    "pool_ratios": [0.5, 0.7, 0.5, 0.5],
    "temperatures": [2.0, 2.0, 100.0, 100.0]
}

device = torch.device("cpu")

print("Loading AASIST model...")

model = Model(model_config)

model.load_state_dict(
    torch.load(
        "aasist/AASIST.pth",
        map_location=device
    )
)

model.to(device)
model.eval()

print("AASIST model loaded successfully!\n")


# -----------------------------
# Settings
# -----------------------------
audio_folder = "audio"
target_length = 64600

# Number of segments per audio
number_of_segments = 4


# -----------------------------
# Test each audio
# -----------------------------
for filename in sorted(os.listdir(audio_folder)):

    if not filename.lower().endswith(".wav"):
        continue

    file_path = os.path.join(audio_folder, filename)

    print("\n" + "=" * 60)
    print("FILE:", filename)
    print("=" * 60)

    # Preprocess
    audio, sample_rate = preprocess_audio(file_path)

    total_samples = len(audio)

    spoof_scores = []

    # Calculate segment positions
    if total_samples < target_length:

        segments = [audio]

    else:

        max_start = total_samples - target_length

        if number_of_segments == 1:
            starts = [0]
        else:
            starts = np.linspace(
                0,
                max_start,
                number_of_segments,
                dtype=int
            )

        segments = [
            audio[start:start + target_length]
            for start in starts
        ]


    # -----------------------------
    # Run AASIST on each segment
    # -----------------------------
    for i, segment in enumerate(segments):

        # If segment is short, repeat it
        if len(segment) < target_length:

            repeats = int(
                np.ceil(target_length / len(segment))
            )

            segment = np.tile(
                segment,
                repeats
            )[:target_length]


        # Convert to tensor
        audio_tensor = torch.tensor(
            segment,
            dtype=torch.float32
        ).unsqueeze(0)

        audio_tensor = audio_tensor.to(device)


        # AASIST prediction
        with torch.no_grad():

            hidden, output = model(audio_tensor)


        probabilities = torch.softmax(
            output,
            dim=1
        )[0]


        # Class 0 = spoof
        # Class 1 = bonafide
        spoof_probability = probabilities[0].item()
        genuine_probability = probabilities[1].item()

        spoof_scores.append(spoof_probability)


        print(
            f"Segment {i + 1}: "
            f"Spoof = {spoof_probability * 100:.2f}% | "
            f"Genuine = {genuine_probability * 100:.2f}%"
        )


    # -----------------------------
    # Average score
    # -----------------------------
    average_spoof = np.mean(spoof_scores)
    average_genuine = 1 - average_spoof


    if average_spoof >= average_genuine:

        prediction = "SPOOF"

    else:

        prediction = "BONAFIDE"


    print("\nFINAL RESULT")
    print("-" * 40)

    print("Prediction    :", prediction)
    print(
        "Average Spoof :",
        f"{average_spoof * 100:.2f}%"
    )
    print(
        "Average Genuine:",
        f"{average_genuine * 100:.2f}%"
    )


print("\n" + "=" * 60)
print("MULTI-SEGMENT TESTING COMPLETED")
print("=" * 60)