from detect_voice import detect_voice

audio_files = [
    "audio/ai1.wav",
    "audio/ai2.wav",
    "audio/real1.wav",
    "audio/real2.wav"
]

for audio_path in audio_files:

    print("\n" + "=" * 50)
    print("FILE:", audio_path)
    print("=" * 50)

    result = detect_voice(audio_path)

    print("Prediction    :", result["prediction"])
    print("Spoof Score   :", result["spoof_score"])
    print("Genuine Score :", result["genuine_score"])