import soundfile as sf
import numpy as np
import os

folder = "audio"

print("\nAUDIO SIGNAL CHECK")
print("=" * 50)

for filename in sorted(os.listdir(folder)):

    if not filename.endswith(".wav"):
        continue

    path = os.path.join(folder, filename)

    audio, sample_rate = sf.read(
        path,
        dtype="float32",
        always_2d=True
    )

    rms = np.sqrt(np.mean(audio ** 2))
    peak = np.max(np.abs(audio))

    print("\nFile:", filename)
    print("RMS :", f"{rms:.6f}")
    print("Peak:", f"{peak:.6f}")

print("\n" + "=" * 50)