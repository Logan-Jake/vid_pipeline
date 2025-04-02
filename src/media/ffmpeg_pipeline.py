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
        "-i", background_path,  # 0 - background
        "-loop", "1", "-framerate", "25", "-t", "5", "-i", overlay_path,  # 1 - PNG overlay as looped 5s stream
        "-i", audio_path,  # 2 - mixed audio
        "-filter_complex", "[1:v] scale=iw*0.9:ih*0.9 [overlay]; [0:v][overlay] overlay=x=("
                           "main_w-overlay_w)/2:y=80:enable='lte(t,5)':format=auto",
        "-map", "0:v", "-map", "2:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",  # ✅ Windows compatibility
        "-preset", "ultrafast",#"slow",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    print("🚀 FFmpeg command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)
