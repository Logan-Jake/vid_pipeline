import subprocess
import shutil
from pathlib import Path

def ffmpeg_compose_video(background_path, overlay_path, audio_path, output_path):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found in PATH")

    print("🔍 Validating FFmpeg inputs:")
    print(" - Background video exists:", Path(background_path).exists(), background_path)
    print(" - Overlay graphic exists:", Path(overlay_path).exists(), overlay_path)
    print(" - Final audio exists:", Path(audio_path).exists(), audio_path)

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", background_path,                   # Input 0: background video
        "-loop", "1", "-t", "5", "-i", overlay_path,  # Input 1: image as 5s video
        "-i", audio_path,                         # Input 2: final mixed audio
        "-filter_complex", "[0:v][1:v] overlay=(W-w)/2:50:enable='lte(t,5)'",  # overlay for first 5s
        "-map", "0:v", "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    print("🚀 FFmpeg command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)
