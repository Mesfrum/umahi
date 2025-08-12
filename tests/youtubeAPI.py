import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get API key from environment
api_key = os.getenv("YT_API_KEY")

if not api_key:
    raise ValueError(
        "YouTube API key not found. Please set YT_API_KEY in your .env file."
    )

# Build YouTube service
youtube = build("youtube", "v3", developerKey=api_key)

# Make request
req = youtube.search().list(q="tech news", part="snippet", maxResults=5)
res = req.execute()

# Print video titles
for item in res.get("items", []):
    print(item["snippet"]["title"])
