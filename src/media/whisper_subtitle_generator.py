import whisper
import textwrap
import sys
import os

# Set TORCH_HOME to a directory inside your virtual environment
os.environ["TORCH_HOME"] = os.path.join(os.path.dirname(sys.executable), "whisper_cache")

# Maximum words per subtitle chunk and wrap width
MAX_WORDS = 7
WRAP_WIDTH = 40


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds (float) to SRT timestamp format HH:MM:SS,mmm.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def generate_subtitle_from_voiceover(voiceover_path: str, subtitle_path: str, model_size: str = "small"):
    """
    Transcribe the voiceover and write a post-processed SRT with shorter segments.

    :param voiceover_path: Path to the voiceover audio file.
    :param subtitle_path: Path where the generated subtitle file (SRT) will be saved.
    :param model_size: Whisper model size ("tiny", "base", "small", "medium", "large").
    """
    # Load model and transcribe
    model = whisper.load_model(model_size)
    result = model.transcribe(voiceover_path)
    segments = result.get("segments", [])
    if not segments:
        print("No transcription segments found.")
        return

    idx = 1
    with open(subtitle_path, "w", encoding="utf-8") as srt_file:
        for segment in segments:
            start, end = segment["start"], segment["end"]
            words = segment["text"].strip().split()
            # split into chunks of <= MAX_WORDS
            chunks = [words[i:i+MAX_WORDS] for i in range(0, len(words), MAX_WORDS)]
            # divide duration equally
            duration = end - start
            chunk_dur = duration / len(chunks)
            for j, chunk in enumerate(chunks):
                chunk_start = start + j * chunk_dur
                chunk_end = chunk_start + chunk_dur
                text = " ".join(chunk)
                srt_file.write(f"{idx}\n")
                srt_file.write(f"{format_timestamp(chunk_start)} --> {format_timestamp(chunk_end)}\n")
                # wrap text lines
                for line in textwrap.wrap(text, width=WRAP_WIDTH):
                    srt_file.write(line + "\n")
                srt_file.write("\n")
                idx += 1

    print(f"Subtitle file generated at: {subtitle_path}")

