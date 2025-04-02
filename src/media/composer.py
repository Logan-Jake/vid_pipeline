from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip as CompositeClip
from moviepy.video.VideoClip import ImageClip
from media.music_fetcher import download_random_track
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


# def compose_video(voiceover_path: str, graphic_path: str, background_path: str, output_name: str = None) -> str:
#     if output_name is None:
#         output_name = get_next_video_filename()
#
#     output_path = Path(__file__).parent / "output" / output_name
#     output_path.parent.mkdir(parents=True, exist_ok=True)
#
#     # Load main clips
#     audio = AudioFileClip(voiceover_path)
#     bg_video = VideoFileClip(background_path).resized((1080, 1920)).subclipped(0, audio.duration)
#
#
#     # Load music
#     music = download_random_track()#.subclipped(0, audio.duration).max_volume(0.1)
#     print("🎧 audio:", type(audio))
#     print("🎵 music:", type(music))
#     mixed_audio = CompositeAudioClip([audio, music])
#     bg_video = bg_video.with_audio(mixed_audio)
#
#     # Load overlay
#     graphic = ImageClip(graphic_path).with_duration(audio.duration).resized(width=900).with_position(("center", "top"))

    #final = CompositeClip([bg_video, graphic])
    # final.write_videofile(str(output_path), codec="libx264", audio_codec="aac",threads=4) # better qualty

    def mix_audio_tracks(voiceover_path: str, music_path: str, output_path: str):
        voiceover = AudioFileClip(voiceover_path)
        music = AudioFileClip(music_path).with_duration(voiceover.duration).with_volume(0.1)

        final_audio = CompositeAudioClip([voiceover, music])
        final_audio.write_audiofile(output_path)

    return str(output_path)
