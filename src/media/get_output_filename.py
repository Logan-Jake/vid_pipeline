from pathlib import Path

def get_next_video_filename(folder: str = "output", prefix: str = "video_", ext: str = ".mp4") -> str:
    output_dir = Path.cwd() / folder  # ✅ use the working directory
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(output_dir.glob(f"{prefix}*{ext}"))
    if not existing:
        return f"{prefix}001{ext}"

    last_num = max([
        int(f.stem.replace(prefix, "")) for f in existing
        if f.stem.replace(prefix, "").isdigit()
    ])
    return f"{prefix}{last_num + 1:03d}{ext}"