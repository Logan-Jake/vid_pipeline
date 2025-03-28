from pathlib import Path
import random
from moviepy.audio.io.AudioFileClip import AudioFileClip

def get_random_music(path: str = "assets/music") -> AudioFileClip:
    folder = Path(path)
    tracks = list(folder.glob("*.mp3")) + list(folder.glob("*.wav"))
    if not tracks:
        raise FileNotFoundError("No background music found.")
    selected = random.choice(tracks)
    return AudioFileClip(str(selected))