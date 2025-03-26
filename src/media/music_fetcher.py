import requests
import random
from pathlib import Path
from moviepy.editor import AudioFileClip


def download_random_track() -> AudioFileClip:
    # Sample Pixabay track URLs (rotate these or scrape more later)
    tracks = [
        "https://cdn.pixabay.com/audio/2022/03/15/audio_96b731bb02.mp3",
        "https://cdn.pixabay.com/audio/2023/03/20/audio_187f0a576e.mp3",
        "https://cdn.pixabay.com/audio/2023/05/30/audio_e6f865dd61.mp3"
    ]
    url = random.choice(tracks)

    response = requests.get(url)
    response.raise_for_status()

    temp_path = Path("output") / "temp_music.mp3"
    with open(temp_path, "wb") as f:
        f.write(response.content)

    return AudioFileClip(str(temp_path))
