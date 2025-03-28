
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing import CompositeVideoClip
from moviepy.video.VideoClip import ImageClip
from media.music_fetcher import download_random_track
from media.music_utils import get_random_music
from pathlib import Path
import random


def get_next_video_filename(folder: str = "output", prefix: str = "video_", ext: str = ".mp4") -> str:
    output_dir = Path(folder)
    output_dir.mkdir(exist_ok=True)

    existing = sorted(output_dir.glob(f"{prefix}*{ext}"))
    if not existing:
        return f"{prefix}001{ext}"

    last_num = max([
        int(f.stem.replace(prefix, "")) for f in existing
        if f.stem.replace(prefix, "").isdigit()
    ])
    return f"{prefix}{last_num + 1:03d}{ext}"


def compose_video(voiceover_path: str, graphic_path: str, background_path: str, output_name: str = "final_video.mp4") -> str:
    output_path = Path("output") / output_name

    # Load video and voiceover
    audio = AudioFileClip(voiceover_path)
    bg_video = VideoFileClip(background_path).resized((1080, 1920)).subclipped(0, audio.duration)

    # Load music and mix it quietly under the voice
    try:
        music = download_random_track()
    except Exception as e:
        print("⚠️ Failed to download music, falling back to local:", e)
        music = get_random_music()

    if music is None:
        raise RuntimeError("No music could be loaded.")

    music = music.subclipped(0, audio.duration)
    music = music.set_audio(music.audio.set_volume(0.1))
    mixed_audio = CompositeAudioClip([audio, music])
    bg_video = bg_video.set_audio(mixed_audio)

    # Load graphic and overlay
    graphic = ImageClip(graphic_path).set_duration(audio.duration).resize(width=900).set_position(("center", "top"))
    final = CompositeVideoClip([bg_video, graphic])

    # Render to file (debug AVI version)
    final.write_videofile(str(output_path.with_suffix(".avi")), codec="png", audio_codec="aac")
    return str(output_path)
