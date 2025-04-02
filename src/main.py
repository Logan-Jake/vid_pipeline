from reddit.fetcher import fetch_top_story
from media.tts import generate_voiceover
from media.graphic_gen import generate_post_bubble
from media.get_output_filename import get_next_video_filename
from media.audio_mixer import mix_audio_tracks  # ⬅️ added mix_audio_tracks
from media.footage_finder import get_random_background
from media.music_fetcher import download_random_track  # ⬅️ needed for music
from media.ffmpeg_pipeline import ffmpeg_compose_video  # ⬅️ new FFmpeg final step
from pathlib import Path
import os

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
    print("🖼 Profile Pic URL:", story['profile_pic_url'])

    try:
        # Generate graphic
        graphic_path = generate_post_bubble(
            title=story['title'],
            author=story['author'],
            score=story['score'],
            profile_pic_url=story['profile_pic_url'],
            awards=story['awards']
        )
        print(f"🖼 Graphic saved to: {graphic_path}")
    except Exception as e:
        print("❌ Error generating graphic:")
        import traceback
        traceback.print_exc()

    # Generate voiceover
    voice_path = generate_voiceover(story['text'] or story['title'])
    print(f"🎤 Voiceover saved to: {voice_path}")

    # Select background + filename
    bg_path = get_random_background()
    filename = get_next_video_filename()

    final_audio_path = "output/final_audio.mp3"
    music_clip = download_random_track()
    music_path = music_clip.filename if hasattr(music_clip, "filename") else music_clip

    # Step 1: Mix voiceover + music into MP3
    mix_audio_tracks(voice_path, music_path, final_audio_path)

    print("🔍 Validating FFmpeg inputs:")
    print(" - Background video exists:", Path(bg_path).exists(), bg_path)
    print(" - Overlay graphic exists:", Path(graphic_path).exists(), graphic_path)
    print(" - Final audio exists:", Path(final_audio_path).exists(), final_audio_path)

    # Step 2: Use FFmpeg to overlay graphic and add audio
    final_path = f"output/{filename}"
    ffmpeg_compose_video(
        background_path=bg_path,
        overlay_path=graphic_path,
        audio_path=final_audio_path,
        output_path=final_path
    )


    print(f"🎬 Final video saved to: {final_path}")

    try:
        os.remove(voice_path)
        os.remove(graphic_path)
        os.remove(final_audio_path)
        print("🧹 Cleaned up temporary files.")
    except Exception as e:
        print("⚠️ Failed to delete some temporary files:", e)


