import sys
import os
from pathlib import Path

# Set TORCH_HOME to a directory inside your virtual environment
os.environ["TORCH_HOME"] = os.path.join(os.path.dirname(sys.executable), "whisper_cache")

from reddit.fetcher import fetch_top_story
from media.tts import generate_voiceover # replaced by elevenlabs
# from media.elevenlabs_tts import generate_voiceover  # text to speech
# from media.f5_tts import generate_voiceover  # text to speech
from media.graphic_gen import generate_post_bubble  # Generates graphic
from media.get_output_filename import get_next_video_filename
from media.audio_mixer import mix_audio_tracks  # added mix_audio_tracks
from media.footage_fetcher import get_random_background  # Fetches background video, not working yet
from media.music_fetcher import download_random_track  # needed for music, but doesn't work yet
from media.ffmpeg_pipeline import ffmpeg_compose_video_with_subs  # ffmpeg final step, builds the video
# from media.whisper_subtitle_generator import generate_subtitle_from_voiceover
# from media.vosk_subtitle_generator import generate_subtitle_from_voiceover
from media.subtitle_processing import make_ass
from moviepy.audio.io.AudioFileClip import AudioFileClip

if __name__ == "__main__":
    story = fetch_top_story()

    if not story:
        print("No suitable story found.")
        exit()

    print("🎉 Story Fetched:")
    print(f"Title: {story['title']}")
    print(f"By: u/{story['author']} ({story['score']} upvotes)")
    print("-----")
    print(story['text'])
    #print("🖼 Profile Pic URL:", story['profile_pic_url'])

    bubble_template = Path(__file__).parent.parent / "src" / "assets" / "Reddit_card.png"  # default graphic location

    try:
        graphic_path = generate_post_bubble(
            image_path=bubble_template,
            title=story["title"],
            # output_path="out/my_titled_image.png"  # optionally override
        )
        print(f"🖼 Graphic saved to: {graphic_path}")
    except Exception as e:
        print("❌ Error generating graphic:")
        import traceback

        traceback.print_exc()

    # Generate voiceover
    title_path = generate_voiceover(story["title"], filename="title.wav")
    story_path = generate_voiceover(story["text"], filename="story.wav")
    voice_path = generate_voiceover(story['text'] or story['title'])
    print(f"🎤 Voiceover saved to: {voice_path}")

    # Generate subtitles from the voiceover using Whisper
    # subtitle_path = "output/subtitles.srt"
    # if not generate_subtitle_from_voiceover(voice_path, subtitle_path):
    #     print("⚠️ Subtitle generation failed. Exiting...")
        # exit()

    # Generate timed+positioned ASS file
    ass_path = "output/highlight.ass"
    title_duration = AudioFileClip(title_path).duration
    make_ass(story_path, ass_path, delay=title_duration)
    subtitle_path = ass_path  # feed ASS into ffmpeg

    # Select background + filename
    bg_path = get_random_background()
    filename = get_next_video_filename()

    final_audio_path = "output/final_audio.mp3"
    music_clip = download_random_track()
    music_path = music_clip.filename if hasattr(music_clip, "filename") else music_clip

    # Step 1: Mix voiceover + music into MP3
    mix_audio_tracks([title_path, story_path], music_path, final_audio_path)

    # Step 2: Use FFmpeg to overlay graphic and add audio
    final_path = f"output/{filename}"
    ffmpeg_compose_video_with_subs(
        background_path=bg_path,
        overlay_path=graphic_path,
        audio_path=final_audio_path,
        subtitles_path=subtitle_path,
        output_path=final_path
    )

    print(f"🎬 Final video saved to: {final_path}")

    try:
        os.remove(voice_path)
        os.remove(graphic_path)
        os.remove(final_audio_path)
        os.remove(subtitle_path)
        print("🧹 Cleaned up temporary files.")
    except Exception as e:
        print("⚠️ Failed to delete some temporary files:", e)

