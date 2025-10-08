import json
import subprocess

def run_yt_dlp(url: str):
    """Run yt-dlp and return parsed video JSON list."""
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

def fetch_shorts():
    print("Fetching from YouTube Trending Shorts...")
    trending_url = "https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl"
    videos = run_yt_dlp(trending_url)

    # Fallback to search if trending feed is empty
    if not videos:
        print("No Shorts found in trending feed. Trying search-based fallback...")
        search_url = "https://www.youtube.com/results?search_query=shorts&sp=EgIYAQ%3D%3D"
        videos = run_yt_dlp(search_url)

    if not videos:
        print("No videos found at all.")
        return

    # Filter: Only include videos <= 60 seconds if duration info is available
    filtered = [v for v in videos if v.get("duration") is None or v["duration"] <= 60]

    with open("queue.json", "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Saved {len(filtered)} videos to queue.json")

if __name__ == "__main__":
    fetch_shorts()
