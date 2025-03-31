from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip as CompositeClip
from moviepy.video.VideoClip import ImageClip
from media.music_fetcher import download_random_track
from media.music_utils import get_random_music
from pathlib import Path


def get_next_video_filename(folder: str = "output", prefix: str = "video_", ext: str = ".mp4") -> str:
    output_dir = Path(__file__).parent / folder
    output_dir.mkdir(exist_ok=True)

    existing = sorted(output_dir.glob(f"{prefix}*{ext}"))
    if not existing:
        return f"{prefix}001{ext}"

    last_num = max([
        int(f.stem.replace(prefix, "")) for f in existing
        if f.stem.replace(prefix, "").isdigit()
    ])
    return f"{prefix}{last_num + 1:03d}{ext}"


def compose_video(voiceover_path: str, graphic_path: str, background_path: str, output_name: str = "final_video.avi") -> str:
    output_path = Path(__file__).parent / "output" / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load audio and background video
    audio = AudioFileClip(voiceover_path)
    bg_video = VideoFileClip(background_path).resized((1080, 1920)).subclipped(0, audio.duration)

    # Optional music (currently commented out)
    try:
        music = download_random_track()
    except Exception as e:
        print("⚠️ Failed to download music, falling back to local:", e)
        music_path = get_random_music()
        music = AudioFileClip(music_path)

    if music is None:
        raise RuntimeError("No music could be loaded.")

    # Adjust music volume and combine audio tracks
    music = music.subclipped(0, audio.duration).max_volume(0.1)
    mixed_audio = CompositeAudioClip([audio, music])
    bg_video = bg_video.set_audio(mixed_audio)

    # Load overlay graphic
    graphic = ImageClip(graphic_path).with_duration(audio.duration).resized(width=900).with_position(("center", "top"))

    # Combine video and overlay
    final = CompositeClip([bg_video, graphic])

    # Write the output video
    final.write_videofile(str(output_path), codec="libx264", audio_codec="aac")

    return str(output_path)
