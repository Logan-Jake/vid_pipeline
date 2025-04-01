from reddit.fetcher import fetch_top_story
from media.tts import generate_voiceover
from media.graphic_gen import generate_post_bubble
from media.composer import compose_video, get_next_video_filename
from media.footage_finder import get_random_background

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

    # Compose final video
    final_path = compose_video(
        voiceover_path=voice_path,
        graphic_path=graphic_path,
        background_path=bg_path,
        output_name=filename
    )
    print(f"🎬 Final video saved to: {final_path}")

