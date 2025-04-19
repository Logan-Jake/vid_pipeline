import subprocess, sys
from pathlib import Path
import soundfile as sf
import resampy
import wave

BASE = Path(__file__).parent.parent / "media" / "output"
BASE.mkdir(parents=True, exist_ok=True)

def generate_voiceover(text: str):
    temp = BASE / "voice_temp.wav"
    final = BASE / "voiceover.wav"

    # build cmd
    cli = Path(sys.exec_prefix) / "Scripts" / "f5-tts_infer-cli.exe"
    cmd = [str(cli),
           "--gen_text", text,
           "-w", str(temp),
           "--vocoder_name", "vocos",
           "--nfe_step", "20",
           "--cfg_strength", "0.4",
           "--cross_fade_duration", "0.02",
           "--fix_duration", "1.0",
           "--speed", "0.95"]

    print("Running TTS CLI:", " ".join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("TTS STDOUT:\n", proc.stdout)
    print("TTS STDERR:\n", proc.stderr)
    proc.check_returncode()

    # quick WAV‐header check
    print("Temp WAV:", temp.resolve(), "Exists?", temp.exists(), "Size:", temp.stat().st_size)
    if temp.exists():
        with wave.open(str(temp),"rb") as wf:
            print(" >> nch:", wf.getnchannels(),
                  "rate:", wf.getframerate(),
                  "frames:", wf.getnframes())

    # convert to mono16
    data, sr = sf.read(str(temp))
    if data.ndim>1: data = data.mean(axis=1)
    data16 = resampy.resample(data, sr, 16000)
    sf.write(str(final), data16, 16000, subtype="PCM_16")

    # final check
    print("Final WAV:", final.resolve(), "Size:", final.stat().st_size)
    return str(final.resolve())
