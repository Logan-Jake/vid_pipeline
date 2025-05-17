import subprocess
import shutil
import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pathlib import Path

def ffmpeg_compose_video_with_subs(background_path, overlay_path, audio_path, subtitles_path, output_path, title_duration):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found in PATH")

    print(f"✅ Subtitle file found: {subtitles_path} ({os.path.getsize(subtitles_path)} bytes)")

    fonts_dir = Path(__file__).resolve().parent / ".." / "assets" / "fonts"
    fonts_dir = fonts_dir.resolve()

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", background_path,  # Input 0: Background video
        "-loop", "1", "-framerate", "25", "-t", "0.1", "-i", overlay_path,  # Input 1: Looping overlay PNG
        "-i", audio_path,  # Input 2: Audio
        "-filter_complex",
        (
            "[1:v] scale=iw*1.2:ih*1.2 [overlay]; "  # Scale the overlay image
            f"[0:v][overlay] overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='lte(t,{title_duration})' [vid_with_overlay]; "
            f"[vid_with_overlay] ass= " + subtitles_path + "  [video_out]"

        ),
        "-map", "[video_out]",  # Map the final video (with subtitles)
        "-map", "2:a",          # Map the audio
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",  # For Windows compatibility
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",

        output_path
    ]


    subprocess.run(cmd, check=True)
