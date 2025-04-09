from moviepy.audio.io.AudioFileClip import AudioFileClip
from media.music_utils import get_random_music
from pathlib import Path

def download_random_track():
    try:
        # Attempt online download (skipping here for now)
        raise Exception("Force fallback for testing")
    except Exception as e:
        print("⚠️ Failed to download music:", e)

        fallback = get_random_music()
        # print("🎵 Fallback type:", type(fallback))
        # print("🎵 Fallback value:", fallback)

        if isinstance(fallback, (str, Path)):
            fallback_path = str(fallback)
            if not Path(fallback_path).exists():
                raise FileNotFoundError(f"Fallback music path does not exist: {fallback_path}")
            clip = AudioFileClip(fallback_path)

            # ✅ Validate it's an AudioFileClip with duration & fps
            # print("🔍 Loaded fallback AudioFileClip:")
            # print("    - duration:", clip.duration)
            # print("    - fps:", clip.fps)
            # print("    - class:", type(clip))

            return clip

        elif isinstance(fallback, AudioFileClip):
            return fallback

        else:
            raise TypeError(f"get_random_music() returned invalid type: {type(fallback)}")


#download_random_track()
