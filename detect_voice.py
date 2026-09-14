import sys
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

TARGET_LENGTH = 64600
device = torch.device("cpu")


# -----------------------------
# Load AASIST model
# -----------------------------
model = Model(model_config)

model.load_state_dict(
    torch.load(
        "aasist/AASIST.pth",
        map_location=device
    )
)

model.to(device)
model.eval()


# -----------------------------
# Voice detection function
# -----------------------------
def detect_voice(audio_path):

    # Preprocess audio
    audio, sample_rate = preprocess_audio(audio_path)

    total_samples = len(audio)

    # Create multiple segments
    if total_samples < TARGET_LENGTH:

        segments = [audio]

    else:

        max_start = total_samples - TARGET_LENGTH

        starts = np.linspace(
            0,
            max_start,
            4,
            dtype=int
        )

        segments = [
            audio[start:start + TARGET_LENGTH]
            for start in starts
        ]


    spoof_scores = []


    # -----------------------------
    # Analyze each segment
    # -----------------------------
    for segment in segments:

        # Repeat short audio if necessary
        if len(segment) < TARGET_LENGTH:

            repeats = int(
                np.ceil(TARGET_LENGTH / len(segment))
            )

            segment = np.tile(
                segment,
                repeats
            )[:TARGET_LENGTH]


        # Convert to tensor
        audio_tensor = torch.tensor(
            segment,
            dtype=torch.float32
        ).unsqueeze(0)

        audio_tensor = audio_tensor.to(device)


        # AASIST inference
        with torch.no_grad():

            _, output = model(audio_tensor)


        # Class 0 = spoof
        # Class 1 = bonafide
        probabilities = torch.softmax(
            output,
            dim=1
        )[0]

        spoof_score = probabilities[0].item()

        spoof_scores.append(spoof_score)


    # -----------------------------
    # Calculate average
    # -----------------------------
    average_spoof = float(
        np.mean(spoof_scores)
    )

    average_genuine = 1 - average_spoof


    # -----------------------------
    # Final prediction
    # -----------------------------
    if average_spoof >= average_genuine:

        prediction = "SPOOF"

    else:

        prediction = "BONAFIDE"


    # -----------------------------
    # Return result
    # -----------------------------
    return {
        "prediction": prediction,
        "spoof_score": round(
            average_spoof * 100,
            2
        ),
        "genuine_score": round(
            average_genuine * 100,
            2
        )
    }


# -----------------------------
# Test the module
# -----------------------------
if __name__ == "__main__":
    result = detect_voice("audio/ai1.wav")
    print("\nNEXORA Voice Detection Result")
    print("--------------------------------")
    print("Prediction    :", result["prediction"])
    print("Spoof Score   :", result["spoof_score"], "%")
    print("Genuine Score :", result["genuine_score"], "%")