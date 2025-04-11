from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

elevenlabs_key='sk_3bee053a11745f6d19c7ea1a2bc439ea30ca98798f8bd137'

