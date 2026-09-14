import soundfile as sf
import os

folder = "audio"

for file in os.listdir(folder):

    if file.endswith(".wav"):

        path = os.path.join(folder, file)

        audio, sample_rate = sf.read(path)

        print("\nFile:", file)
        print("Sample Rate:", sample_rate)
        print("Channels:", 1 if len(audio.shape) == 1 else audio.shape[1])
        print("Duration:", len(audio) / sample_rate, "seconds")