import whisper

import os
os.environ["TORCH_HOME"] = os.path.join(os.path.dirname(__file__), "model_cache")

voiceover_file = "output/final_audio.mp3"
subtitle_file = "output/subtitles.srt"
# model_size = "small"                         # Options include "tiny", "base", "small", "medium",
def format_timestamp(seconds: float) -> str:
    """
    Convert seconds (float) to SRT timestamp format HH:MM:SS,mmm.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def generate_subtitle_from_voiceover(voiceover_path: str, subtitle_path: str, model_size: str = "medium"):
    """
    Transcribe the voiceover audio and write the transcription as an SRT file.

    :param voiceover_path: Path to the voiceover audio file.
    :param subtitle_path: Path where the generated subtitle file (SRT) will be saved.
    :param model_size: Size of the Whisper model to use ("tiny", "base", "small", "medium", "large").
    """
    try:
        # Load the Whisper model; "base" is a good balance between speed and quality
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"Error loading Whisper model '{model_size}': {e}")
        return

    try:
        # Transcribe the audio; the result contains a list of segments with timings and text
        result = model.transcribe(voiceover_path)
    except Exception as e:
        print(f"Error transcribing the audio file '{voiceover_path}': {e}")
        return

    segments = result.get("segments")
    if not segments:
        print("No transcription segments found. Please check the input file or try a different model size.")
        return

    try:
        # Write out the SRT file
        with open(subtitle_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(segments, start=1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{text}\n\n")
    except Exception as e:
        print(f"Error writing SRT file to '{subtitle_path}': {e}")
        return

    print(f"Subtitle file generated at: {subtitle_path}")

# Example usage:
# generate_subtitle_from_voiceover("path/to/voiceover.mp3", "path/to/subtitles.srt")
