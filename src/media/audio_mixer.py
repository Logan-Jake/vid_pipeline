from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from pathlib import Path
import math


def mix_audio_tracks(voice_paths: list, music_path: str, output_path: str):
    print("Mixing audio tracks...")

    voices = [AudioFileClip(p) for p in voice_paths]
    voiceover = concatenate_audioclips(voices)

    music = AudioFileClip(music_path)
    if music.duration < voiceover.duration:
        loops_required = math.ceil(voiceover.duration / music.duration)
        print(f"   🔁 Looping music {loops_required} times")
        music = concatenate_audioclips([music] * loops_required)

    music = music.subclipped(0, voiceover.duration).with_volume_scaled(0.05)
    mixed_audio = CompositeAudioClip([voiceover, music])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing mixed audio to: {output_path}")
    mixed_audio.write_audiofile(str(output_path), fps=44100, codec='libmp3lame')

    for clip in voices + [music, mixed_audio]:
        clip.close()

    # Prevent WinError 6
    voiceover.close()
    music.close()
    mixed_audio.close()
