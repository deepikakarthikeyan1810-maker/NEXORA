import sys
import os
import torch
import numpy as np

sys.path.append("aasist")

from AASIST import Model
from preprocess import preprocess_audio


model_config = {
    "nb_samp": 64600,
    "first_conv": 128,
    "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
    "gat_dims": [64, 32],
    "pool_ratios": [0.5, 0.7, 0.5, 0.5],
    "temperatures": [2.0, 2.0, 100.0, 100.0]
}

device = torch.device("cpu")

print("Loading AASIST...")

model = Model(model_config)

checkpoint = torch.load(
    "aasist/AASIST.pth",
    map_location=device
)

model.load_state_dict(checkpoint)
model.to(device)
model.eval()

print("Model loaded successfully!\n")

TARGET_LENGTH = 64600
AUDIO_FOLDER = "audio"

for filename in sorted(os.listdir(AUDIO_FOLDER)):

    if not filename.lower().endswith(".wav"):
        continue

    print("=" * 60)
    print("FILE:", filename)
    print("=" * 60)

    audio_path = os.path.join(AUDIO_FOLDER, filename)

    audio, sample_rate = preprocess_audio(audio_path)

    # Take first 4 seconds
    if len(audio) < TARGET_LENGTH:

        repeats = int(np.ceil(TARGET_LENGTH / len(audio)))

        audio = np.tile(
            audio,
            repeats
        )[:TARGET_LENGTH]

    else:

        audio = audio[:TARGET_LENGTH]

    audio_tensor = torch.tensor(
        audio,
        dtype=torch.float32
    ).unsqueeze(0)

    with torch.no_grad():

        hidden, output = model(audio_tensor)

    probabilities = torch.softmax(
        output,
        dim=1
    )[0]

    class_0 = probabilities[0].item()
    class_1 = probabilities[1].item()

    print("Raw output :", output)
    print("Class 0    :", f"{class_0 * 100:.2f}%")
    print("Class 1    :", f"{class_1 * 100:.2f}%")

    if class_0 > class_1:
        print("Prediction :", "SPOOF")
    else:
        print("Prediction :", "BONAFIDE")

    print()


print("=" * 60)
print("RAW AASIST TEST COMPLETED")
print("=" * 60)