from moviepy.editor import *
from media.music_fetcher import download_random_track
from pathlib import Path
import random


def get_random_music(path: str = "assets/music") -> AudioFileClip:
    folder = Path(path)
    tracks = list(folder.glob("*.mp3")) + list(folder.glob("*.wav"))
    if not tracks:
        raise FileNotFoundError("No background music found.")
    selected = random.choice(tracks)
    return AudioFileClip(str(selected))


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



# def compose_video(voiceover_path: str, graphic_path: str, background_path: str, output_name: str = "final_video.mp4") -> str:
#     output_path = Path("output") / output_name
#
#     # Load video and voiceover
#     audio = AudioFileClip(voiceover_path)
#     bg_video = VideoFileClip(background_path).resize((1080, 1920)).subclip(0, audio.duration)
#
#     # Load music and mix it quietly under the voice
#     music = download_random_track().volumex(0.1).subclip(0, audio.duration)
#     mixed_audio = CompositeAudioClip([audio, music])
#     bg_video = bg_video.set_audio(mixed_audio)
#
#     # Load graphic and overlay
#     graphic = ImageClip(graphic_path).set_duration(audio.duration).resize(width=900).set_position(("center", "top"))
#     final = CompositeVideoClip([bg_video, graphic])
#
#     #final.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
#     final.write_videofile(str(output_path.with_suffix(".avi"))) #line added to test/debug
#     return str(output_path)

def compose_video(voiceover_path, graphic_path, background_path, output_name="final_video.mp4"):
    output_path = Path("output") / output_name

    audio = AudioFileClip(voiceover_path)
    graphic = ImageClip(graphic_path).set_duration(audio.duration).set_audio(audio)
    graphic = graphic.resize((1080, 1920)).set_position(("center", "top"))

    graphic.write_videofile(str(output_path)/ output_name.replace(".mp4", ".avi"))

    return str(output_path) 