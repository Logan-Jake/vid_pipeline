import random
from pathlib import Path

def get_random_background(path: str = "assets/backgrounds") -> str:
    folder = Path(path)
    print("🔍 Looking for clips in:", folder.resolve())

    clips = list(folder.glob("*.mp4")) + list(folder.glob("*.mov"))
    print("📁 Found video files:", [clip.name for clip in clips])

    if not clips:
        raise FileNotFoundError("No background clips found in assets/backgrounds.")
    return str(random.choice(clips))