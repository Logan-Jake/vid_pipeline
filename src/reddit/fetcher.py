import praw
import requests
from utils import config


# r/relationship_advice, r/AmITheAsshole, r/entitledparents, r/PettyRevenge, r/ProRevenge, r/tifu (Today I Fucked Up)
#  r/MaliciousCompliance, r/TwoHotTakes

def fetch_top_story(subreddit="relationship_advice", min_upvotes=800, min_length=1000, max_length=2800, limit=25,
                    used_ids=None):
    """
    Fetch a top story from Reddit with specified criteria

    Args:
        subreddit: Subreddit name to fetch from
        min_upvotes: Minimum upvotes required
        min_length: Minimum word count
        max_length: Maximum word count
        limit: Number of posts to check
        used_ids: Set of story IDs already used (to avoid duplicates)
    """
    if used_ids is None:
        used_ids = set()

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT
    )

    print(f"Searching r/{subreddit} for stories...")
    print(f"Criteria: {min_upvotes}+ upvotes, {min_length}-{max_length} words")

    checked_count = 0

    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        checked_count += 1

        if submission.stickied:
            print(f"Skipping stickied post: {submission.title[:50]}...")
            continue

        if submission.score < min_upvotes:
            print(f"Skipping low score ({submission.score}): {submission.title[:50]}...")
            continue

        story_text = submission.selftext.strip()
        if not story_text:
            print(f"Skipping text-less post: {submission.title[:50]}...")
            continue

        # Check if we've already used this story
        author_name = str(submission.author)
        story_id = f"{author_name}_{submission.title[:50]}"

        if story_id in used_ids:
            print(f"Skipping already used story: {submission.title[:50]}...")
            continue

        word_count = len(story_text.split())
        if word_count < min_length:
            print(f"Skipping too short ({word_count} words): {submission.title[:50]}...")
            continue

        if word_count > max_length:
            print(f"Skipping too long ({word_count} words): {submission.title[:50]}...")
            continue

        print(f"Found suitable story ({word_count} words, {submission.score} upvotes)")

        # Pull profile pic
        profile_pic_url = None
        try:
            resp = requests.get(f"https://www.reddit.com/user/{author_name}/about.json",
                                headers={"User-Agent": config.REDDIT_USER_AGENT})
            if resp.ok:
                data = resp.json()["data"]
                profile_pic_url = data.get("snoovatar_img") or data.get("icon_img")
        except Exception as e:
            print(f"Profile pic fetch error: {e}")

        # Pull awards
        awards = []
        try:
            for award in submission.all_awardings:
                awards.append({
                    "name": award["name"],
                    "count": award["count"],
                    "icon_url": award["icon_url"]
                })
        except Exception as e:
            print(f"Awards fetch error: {e}")

        return {
            "title": submission.title,
            "text": story_text,
            "author": author_name,
            "score": submission.score,
            "profile_pic_url": profile_pic_url,
            "awards": awards,
            "word_count": word_count,
            "subreddit": subreddit
        }

    print(f"No suitable stories found after checking {checked_count} posts")
    return None