import subprocess
import shutil
from pathlib import Path

def ffmpeg_compose_video_with_subs(background_path, overlay_path, audio_path, subtitles_path, output_path):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found in PATH")

    # print("🔍 Validating FFmpeg inputs:")
    # print(" - Background video exists:", Path(background_path).exists(), background_path)
    # print(" - Overlay graphic exists:", Path(overlay_path).exists(), overlay_path)
    # print(" - Final audio exists:", Path(audio_path).exists(), audio_path)
    # print(" - Subtitles file exists:", Path(subtitles_path).exists(), subtitles_path)

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", background_path,  # Input 0: Background video
        "-loop", "1", "-framerate", "25", "-t", "5", "-i", overlay_path,  # Input 1: Looping overlay PNG
        "-i", audio_path,  # Input 2: Audio
        "-filter_complex",
        (
                "[1:v] scale=iw*0.9:ih*0.9 [overlay]; "
                "[0:v][overlay] overlay=x=(main_w-overlay_w)/2:y=80:enable='lte(t,5)' [vid_with_overlay]; "
                "[vid_with_overlay] subtitles=" + subtitles_path + " [video_out]; "
                "[2:a] volume=1 [aud]" # 👈 reduce audio volume to 30%
        ),
        "-map", "[video_out]",  # Map the final video (with subtitles)
        "-map", "[aud]",  # 👈 Map the filtered audio
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    # print("🚀 FFmpeg command:")
    # print(" ".join(cmd))

    subprocess.run(cmd, check=True)
