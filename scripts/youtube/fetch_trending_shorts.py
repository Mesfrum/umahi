import json
import subprocess
import sys
import urllib.parse

def run_yt_dlp(url: str):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "--add-header", "Accept-Language: en-US,en;q=0.9",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("yt-dlp error:", result.stderr)
        return []
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]

def fetch_shorts(topic=None):
    if topic:
        print(f"Fetching YouTube Shorts for topic: {topic}")
        query = urllib.parse.quote_plus(topic + " shorts")
        url = f"https://www.youtube.com/results?search_query={query}&sp=EgIYAQ%3D%3D"
    else:
        print("Fetching from YouTube Trending Shorts...")
        url = "https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl"

    videos = run_yt_dlp(url)
    if not videos:
        print("No videos found.")
        return

    filtered = [v for v in videos if v.get("duration") is None or v["duration"] <= 60]

    with open("queue.json", "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Saved {len(filtered)} videos to queue.json")

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    fetch_shorts(topic)
