import sys
import os
from pathlib import Path

# Set TORCH_HOME to a directory inside your virtual environment
os.environ["TORCH_HOME"] = os.path.join(os.path.dirname(sys.executable), "whisper_cache")
from reddit.fetcher import fetch_top_story
# from media.tts import generate_voiceover  # replaced by elevenlabs
from media.elevenlabs_tts import generate_voiceover  # text to speech
from media.graphic_gen import generate_post_bubble  # Generates graphic
from media.get_output_filename import get_next_video_filename
from media.audio_mixer import mix_audio_tracks  # added mix_audio_tracks
from media.footage_fetcher import get_random_background  # Fetches background video, not working yet
from media.ffmpeg_pipeline import ffmpeg_compose_video_with_subs  # ffmpeg final step, builds the video
from media.subtitle_processing import make_ass
from moviepy.audio.io.AudioFileClip import AudioFileClip
from media.music_utils import get_random_music

# Reddit configuration
SUBREDDIT_OPTIONS = {
    "1": {"name": "relationship_advice", "display": "Relationship Advice"},
    "2": {"name": "AmITheAsshole", "display": "Am I The Asshole"},
    "3": {"name": "entitledparents", "display": "Entitled Parents"},
    "4": {"name": "PettyRevenge", "display": "Petty Revenge"},
    "5": {"name": "ProRevenge", "display": "Pro Revenge"},
    "6": {"name": "tifu", "display": "Today I Fucked Up"},
    "7": {"name": "MaliciousCompliance", "display": "Malicious Compliance"},
    "8": {"name": "TwoHotTakes", "display": "Two Hot Takes"},
}


class StoryFetcher:
    def __init__(self):
        self.used_story_ids = set()
        self.current_subreddit = "relationship_advice"
        self.min_upvotes = 800
        self.min_length = 1000
        self.max_length = 2800
        self.search_limit = 25

    def configure_settings(self):
        """Configure Reddit fetching settings"""
        print("\nREDDIT SETTINGS")
        print("=" * 40)

        # Subreddit selection
        print("Available subreddits:")
        for key, sub in SUBREDDIT_OPTIONS.items():
            print(f"{key}. r/{sub['name']} - {sub['display']}")

        while True:
            choice = input(
                f"\nSelect subreddit (1-{len(SUBREDDIT_OPTIONS)}) or press Enter for current ({self.current_subreddit}): ").strip()
            if not choice:
                break
            if choice in SUBREDDIT_OPTIONS:
                self.current_subreddit = SUBREDDIT_OPTIONS[choice]["name"]
                break
            print("Invalid choice. Please try again.")

        # Minimum upvotes
        upvotes_input = input(f"Minimum upvotes (current: {self.min_upvotes}): ").strip()
        if upvotes_input.isdigit():
            self.min_upvotes = int(upvotes_input)

        # Word count range
        min_words_input = input(f"Minimum words (current: {self.min_length}): ").strip()
        if min_words_input.isdigit():
            self.min_length = int(min_words_input)

        max_words_input = input(f"Maximum words (current: {self.max_length}): ").strip()
        if max_words_input.isdigit():
            self.max_length = int(max_words_input)

        # Search limit
        limit_input = input(f"Number of posts to check (current: {self.search_limit}): ").strip()
        if limit_input.isdigit():
            self.search_limit = int(limit_input)

        print(f"\nSettings updated:")
        print(f"   Subreddit: r/{self.current_subreddit}")
        print(f"   Min upvotes: {self.min_upvotes}")
        print(f"   Word range: {self.min_length}-{self.max_length}")
        print(f"   Search limit: {self.search_limit}")

    def get_next_story(self):
        story = fetch_top_story(
            subreddit=self.current_subreddit,
            min_upvotes=self.min_upvotes,
            min_length=self.min_length,
            max_length=self.max_length,
            limit=self.search_limit,
            used_ids=self.used_story_ids
        )

        if story:
            # Create a unique ID for this story
            story_id = f"{story['author']}_{story['title'][:50]}"
            self.used_story_ids.add(story_id)
            story['id'] = story_id

        return story

    def reset_used_stories(self):
        """Reset the list of used stories"""
        self.used_story_ids.clear()
        print("Reset story history - can now see previously shown stories again")


def get_story_from_user():
    """Get a custom story from user input"""
    print("\nEnter your custom story:")
    print("Enter the title:")
    title = input("Title: ").strip()

    print("\nEnter the story text (press Enter twice when done):")
    story_lines = []
    empty_line_count = 0

    while True:
        line = input()
        if line == "":
            empty_line_count += 1
            if empty_line_count >= 2:
                break
        else:
            empty_line_count = 0
        story_lines.append(line)

    # Remove trailing empty lines
    while story_lines and story_lines[-1] == "":
        story_lines.pop()

    text = "\n".join(story_lines)

    if not title or not text:
        print("Both title and story text are required!")
        return None

    return {
        'title': title,
        'text': text,
        'author': 'Custom',
        'score': 0,
        'profile_pic_url': None,
        'awards': [],
        'id': f"custom_{title[:50]}"
    }


def display_story(story):
    """Display story details"""
    print("\n" + "=" * 60)
    print("STORY PREVIEW")
    print("=" * 60)
    print(f"Title: {story['title']}")
    print(f"By: u/{story['author']} ({story['score']} upvotes)")
    print(f"Words: {len(story['text'].split())}")
    print("-" * 60)

    # Show first 500 characters with ellipsis if longer
    text_preview = story['text']
    if len(text_preview) > 500:
        text_preview = text_preview[:500] + "..."

    print(text_preview)
    print("=" * 60)


def get_user_choice():
    """Get user's choice for the story"""
    while True:
        print("\nWhat would you like to do?")
        print("1. Use this story")
        print("2. Get another Reddit story")
        print("3. Enter my own story")
        print("4. Configure Reddit settings")
        print("5. Reset story history")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        else:
            print("Invalid choice. Please enter 1-6.")


def get_story_interactive():
    """Interactive story selection process"""
    fetcher = StoryFetcher()

    while True:
        print("\nSTORY SELECTION")
        print("1. Fetch Reddit story")
        print("2. Enter custom story")
        print("3. Configure Reddit settings")
        print("4. Exit")

        initial_choice = input("Enter your choice (1-4): ").strip()

        if initial_choice == '1':
            # Fetch Reddit story
            while True:
                print(f"\nFetching story from r/{fetcher.current_subreddit}...")
                story = fetcher.get_next_story()

                if not story:
                    print("No more suitable stories found with current settings.")
                    print("Try adjusting settings or resetting story history.")
                    break

                display_story(story)

                choice = get_user_choice()

                if choice == '1':
                    return story
                elif choice == '2':
                    # Get another Reddit story - continues the loop
                    continue
                elif choice == '3':
                    # Enter custom story
                    custom_story = get_story_from_user()
                    if custom_story:
                        display_story(custom_story)
                        confirm = input("\nUse this custom story? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes']:
                            return custom_story
                elif choice == '4':
                    # Configure settings
                    fetcher.configure_settings()
                elif choice == '5':
                    # Reset story history
                    fetcher.reset_used_stories()
                elif choice == '6':
                    print("Goodbye!")
                    return None

        elif initial_choice == '2':
            # Enter custom story directly
            custom_story = get_story_from_user()
            if custom_story:
                display_story(custom_story)
                confirm = input("\nUse this custom story? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return custom_story

        elif initial_choice == '3':
            # Configure settings
            fetcher.configure_settings()

        elif initial_choice == '4':
            print("Goodbye!")
            return None
        else:
            print("Invalid choice. Please enter 1-4.")


def process_story(story):
    """Process the selected story into a video"""
    print("\n🎬 PROCESSING VIDEO...")
    print("🎉 Story Selected:")
    print(f"Title: {story['title']}")
    print(f"By: u/{story['author']} ({story['score']} upvotes)")

    bubble_template = Path(__file__).parent.parent / "src" / "assets" / "Reddit_card.png"  # default graphic location

    try:
        graphic_path = generate_post_bubble(
            image_path=bubble_template,
            title=story["title"],
            # output_path="out/my_titled_image.png"  # optionally override
        )
        print(f"🖼 Graphic saved to: {graphic_path}")
    except Exception as e:
        print("Error generating graphic:")
        import traceback
        traceback.print_exc()
        return

    # Generate voiceover
    title_path = generate_voiceover(story["title"], filename="title.wav")
    story_path = generate_voiceover(story["text"], filename="story.wav")
    voice_path = generate_voiceover(story['text'] or story['title'])
    print(f"🎤 Voiceover saved to: {voice_path}")

    # Generate timed+positioned ASS file
    ass_path = "output/highlight.ass"
    title_duration = AudioFileClip(title_path).duration
    make_ass(story_path, ass_path, delay=title_duration + 0.1, max_words_per_line=3)
    subtitle_path = ass_path  # feed ASS into ffmpeg

    # Select background + filename
    bg_path = get_random_background()
    filename = get_next_video_filename()
    final_audio_path = "output/final_audio.mp3"

    # music_clip = download_random_track()
    music_clip = get_random_music()
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
        output_path=final_path,
        title_duration=title_duration
    )

    print(f"🎬 Final video saved to: {final_path}")

    try:
        os.remove(voice_path)
        os.remove(graphic_path)
        os.remove(final_audio_path)
        os.remove(subtitle_path)
        # os.remove()
        print("🧹 Cleaned up temporary files.")
    except Exception as e:
        print("⚠️ Failed to delete some temporary files:", e)


if __name__ == "__main__":
    print("Welcome to the Interactive Story Video Generator!")

    story = get_story_interactive()

    if story:
        process_story(story)
    else:
        print("No story selected. Exiting.")