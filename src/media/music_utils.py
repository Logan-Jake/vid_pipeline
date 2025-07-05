from pathlib import Path
import random

def get_random_music() -> str:
    """Returns the path to a local music file."""
    music_dir = Path(__file__).parent.parent / "assets" / "music"
    tracks = list(music_dir.glob("*.mp3"))
    if not tracks:
        raise FileNotFoundError("No music found.")
    # print(str(random.choice(tracks)))
    return str(random.choice(tracks))


# get_random_music()

