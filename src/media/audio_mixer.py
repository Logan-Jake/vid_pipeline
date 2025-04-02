from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from pathlib import Path
import math

def mix_audio_tracks(voiceover_path: str, music_path: str, output_path: str):
    print("🎧 Mixing audio tracks...")
    print(f"   - Voiceover: {voiceover_path}")
    print(f"   - Music: {music_path}")
    print(f"   - Output: {output_path}")

    voiceover = AudioFileClip(voiceover_path)
    music = AudioFileClip(music_path)

    print("   → voiceover duration:", voiceover.duration)
    print("   → music duration:", music.duration)

    # 🔁 Loop music if it's shorter than voiceover
    if music.duration < voiceover.duration:
        loops_required = math.ceil(voiceover.duration / music.duration)
        print(f"   🔁 Looping music {loops_required} times")
        music = concatenate_audioclips([music] * loops_required)

    # ✂️ Trim music to match voiceover
    music = music.subclipped(0, voiceover.duration)#.with_volume(0.1)

    mixed_audio = CompositeAudioClip([voiceover, music])

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾 Writing mixed audio to: {output_file}")
    mixed_audio.write_audiofile(str(output_file), fps=44100, codec='libmp3lame')
