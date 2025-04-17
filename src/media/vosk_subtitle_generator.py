import sys
import os
import wave
import json
import textwrap
from vosk import Model, KaldiRecognizer

# Path to your Vosk model directory (download from https://alphacephei.com/vosk/models)
VOSK_MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
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


def transcribe_with_vosk(audio_path: str):
    """
    Transcribe WAV/PCM audio using Vosk, returning a list of segments with start, end, text.
    """
    # Ensure file is WAV and mono; if not, user should convert via ffmpeg:
    # ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 32000):
        raise RuntimeError("Audio must be WAV PCM mono with sample rate 8k, 16k, or 32k. Convert with ffmpeg.")

    if not os.path.isdir(VOSK_MODEL_PATH):
        raise FileNotFoundError(f"Vosk model not found at '{VOSK_MODEL_PATH}'. Download and unpack it there.")

    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    segments = []
    raw_results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            raw_results.append(json.loads(rec.Result()))
    raw_results.append(json.loads(rec.FinalResult()))

    # Convert raw Vosk results into intervals
    for res in raw_results:
        words = res.get("result", [])
        if not words:
            continue
        start = words[0]["start"]
        end = words[-1]["end"]
        text = " ".join(w["word"] for w in words)
        segments.append({"start": start, "end": end, "text": text})
    return segments


def generate_subtitle_from_voiceover(audio_path: str, srt_path: str):
    """
    Create an SRT file with short captions by transcribing via Vosk and post-processing.
    """
    segments = transcribe_with_vosk(audio_path)
    if not segments:
        print("No segments returned from Vosk.")
        return

    idx = 1
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for segment in segments:
            start, end, text = segment["start"], segment["end"], segment["text"].strip()
            words = text.split()
            # split into chunks of ≤ MAX_WORDS
            chunks = [words[i:i+MAX_WORDS] for i in range(0, len(words), MAX_WORDS)]
            duration = end - start
            chunk_dur = duration / len(chunks)
            for j, chunk in enumerate(chunks):
                chunk_start = start + j * chunk_dur
                chunk_end = chunk_start + chunk_dur
                line = " ".join(chunk)
                srt_file.write(f"{idx}\n")
                srt_file.write(f"{format_timestamp(chunk_start)} --> {format_timestamp(chunk_end)}\n")
                for wrapped in textwrap.wrap(line, width=WRAP_WIDTH):
                    srt_file.write(wrapped + "\n")
                srt_file.write("\n")
                idx += 1

    print(f"Subtitle file generated at: {srt_path}")



