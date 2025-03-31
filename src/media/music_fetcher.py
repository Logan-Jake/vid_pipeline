
import requests
import random
from pathlib import Path
from moviepy.audio.io.AudioFileClip import AudioFileClip
from media.music_utils import get_random_music

def download_random_track() -> AudioFileClip:
    # Sample Pixabay track URLs (rotate these or scrape more later)
    tracks = [
        "https://cdn.pixabay.com/audio/2022/03/15/audio_96b731bb02.mp3",
        "https://cdn.pixabay.com/audio/2023/03/20/audio_187f0a576e.mp3",
        "https://cdn.pixabay.com/audio/2023/05/30/audio_e6f865dd61.mp3"
    ]
    url = random.choice(tracks)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        return get_random_music()

        # response = requests.get(url, headers=headers)
        # response.raise_for_status()
        #
        # temp_path = Path("output") / "temp_music.mp3"
        # with open(temp_path, "wb") as f:
        #     f.write(response.content)
        #
        # return AudioFileClip(str(temp_path))
    except Exception as e:
        print("⚠️ Failed to download music:", e)
        return get_random_music()
