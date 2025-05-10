import praw
import requests
from utils import config

def fetch_top_story(subreddit="AmITheAsshole", min_upvotes=100, min_length=10, max_length=800):
    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT
    )

    for submission in reddit.subreddit(subreddit).hot(limit=25):
        if submission.stickied or submission.score < min_upvotes:
            continue

        story_text = submission.selftext.strip()
        if not story_text:
            continue

        word_count = len(story_text.split())
        if word_count < min_length or word_count > max_length:
            print(f"⏭ Skipping story with {word_count} words")
            continue

        author_name = str(submission.author)

        # Pull profile pic
        profile_pic_url = None
        try:
            resp = requests.get(f"https://www.reddit.com/user/{author_name}/about.json", headers={"User-Agent": config.REDDIT_USER_AGENT})
            if resp.ok:
                data = resp.json()["data"]
                profile_pic_url = data.get("snoovatar_img") or data.get("icon_img")
        except Exception as e:
            print(f"Profile pic fetch error: {e}")

        # Pull awards
        awards = []
        for award in submission.all_awardings:
            awards.append({
                "name": award["name"],
                "count": award["count"],
                "icon_url": award["icon_url"]
            })

        return {
            "title": submission.title,
            "text": story_text,
            "author": author_name,
            "score": submission.score,
            "profile_pic_url": profile_pic_url,
            "awards": awards
        }

    return None
