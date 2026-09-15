from pathlib import Path
import re
import numpy as np
import torch

from speaker_verification.config import settings
from speaker_verification.preprocessing import load_and_preprocess_audio
from speaker_verification.model import ModelManager
from speaker_verification.embedding import EmbeddingStorage


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

DATASET_DIR = Path("dataset")
EMBEDDING_DIR = Path(settings.embedding_storage_dir)


# ---------------------------------------------------------
# GET SPEAKER ID FROM FILENAME
# ---------------------------------------------------------

def get_speaker_id(filename):
    """
    Extract speaker ID from filenames such as:

    tag_08228_00758955760.wav
    taf_07049_00123456789.wav

    Returns:
        tag_08228
        taf_07049
    """

    match = re.match(r"^(tag|taf)_(\d+)_", filename)

    if match:
        prefix = match.group(1)
        number = match.group(2)
        return f"{prefix}_{number}"

    return None


# ---------------------------------------------------------
# FIND ALL AUDIO FILES
# ---------------------------------------------------------

def collect_audio_files():
    audio_files = []

    for folder in ["realmale", "realfemale"]:
        folder_path = DATASET_DIR / folder

        if not folder_path.exists():
            print(f"WARNING: Folder not found: {folder_path}")
            continue

        for file in folder_path.rglob("*"):
            if file.suffix.lower() in [".wav", ".mp3", ".flac", ".ogg"]:
                audio_files.append(file)

    return audio_files


# ---------------------------------------------------------
# GROUP FILES BY SPEAKER
# ---------------------------------------------------------

def group_by_speaker(audio_files):
    speakers = {}

    for audio_file in audio_files:

        speaker_id = get_speaker_id(audio_file.name)

        if speaker_id is None:
            print(f"WARNING: Could not identify speaker: {audio_file.name}")
            continue

        if speaker_id not in speakers:
            speakers[speaker_id] = []

        speakers[speaker_id].append(audio_file)

    return speakers


# ---------------------------------------------------------
# CREATE SPEAKER EMBEDDING
# ---------------------------------------------------------

def create_speaker_embedding(speaker_id, audio_files, model):
    embeddings = []

    print(f"\nSpeaker: {speaker_id}")
    print(f"Recordings: {len(audio_files)}")

    for audio_file in audio_files:

        print(f"  Processing: {audio_file.name}")

        try:
            # Read and preprocess audio
            audio_bytes = audio_file.read_bytes()

            waveform = load_and_preprocess_audio(audio_bytes)

            # Extract ECAPA-TDNN embedding
            embedding = model.extract_embedding(waveform)

            # Convert to numpy
            embedding = np.asarray(embedding, dtype=np.float32)

            # Flatten
            embedding = embedding.reshape(-1)

            # L2 normalize
            norm = np.linalg.norm(embedding)

            if norm > 0:
                embedding = embedding / norm

            embeddings.append(embedding)

        except Exception as e:
            print(f"  ERROR: {e}")

    if not embeddings:
        print(f"  No valid recordings for {speaker_id}")
        return None

    # -----------------------------------------------------
    # Average all recordings belonging to this speaker
    # -----------------------------------------------------

    speaker_embedding = np.mean(
        np.stack(embeddings),
        axis=0
    )

    # Normalize final speaker embedding
    norm = np.linalg.norm(speaker_embedding)

    if norm > 0:
        speaker_embedding = speaker_embedding / norm

    return speaker_embedding


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("NEXORA SPEAKER DATASET ENROLLMENT")
    print("=" * 60)

    # Create embedding directory
    EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------
    # Load ECAPA-TDNN model
    # -----------------------------------------------------

    print("\nLoading ECAPA-TDNN model...")

    model = ModelManager.get_model()

    print("Model loaded successfully.")

    # -----------------------------------------------------
    # Find audio files
    # -----------------------------------------------------

    print("\nSearching dataset...")

    audio_files = collect_audio_files()

    print(f"Found {len(audio_files)} audio files.")

    if not audio_files:
        print("\nERROR: No audio files found.")
        print("Check that your dataset is inside:")
        print("dataset/realmale/")
        print("dataset/realfemale/")
        return

    # -----------------------------------------------------
    # Group recordings by speaker
    # -----------------------------------------------------

    speakers = group_by_speaker(audio_files)

    print(f"Found {len(speakers)} speaker IDs.")

    # -----------------------------------------------------
    # Create embedding for each speaker
    # -----------------------------------------------------

    storage = EmbeddingStorage()

    successful = 0

    for speaker_id, files in sorted(speakers.items()):

        embedding = create_speaker_embedding(
            speaker_id,
            files,
            model
        )

        if embedding is None:
            continue

        # Save speaker embedding
        storage.save_speaker_embedding(
            speaker_id,
            embedding
        )

        print(f"  SAVED: {speaker_id}.npy")

        successful += 1

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("ENROLLMENT COMPLETED")
    print("=" * 60)

    print(f"Total speaker IDs : {len(speakers)}")
    print(f"Successfully saved: {successful}")
    print(f"Embedding folder  : {EMBEDDING_DIR}")

    print("\nYour enrolled speaker embeddings are ready.")


if __name__ == "__main__":
    main()
