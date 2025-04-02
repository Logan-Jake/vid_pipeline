# ffmpeg_pipeline.py

import subprocess

def ffmpeg_compose_video(
    background_path: str,
    overlay_path: str,
    audio_path: str,
    output_path: str
):
    cmd = [
        "ffmpeg",
        "-i", background_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", "overlay=(W-w)/2:50",  # center top
        "-map", "0:v",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    print("🛠 Running FFmpeg command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)
