import yt_dlp
import json
import os
import subprocess

# Folders
DOWNLOAD_DIR = "downloads"
META_FILE = "metadata.json"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_shorts(url: str):
    ydl_opts = {
        "format": "bv[height<=720]+ba/best[height<=720]",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": False,
        "cookiefile": "/home/akhil/umahi_kalan/scripts/youtube/cookies.txt",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Handle single video vs playlist
        if "entries" in info:
            videos = info["entries"]
        else:
            videos = [info]

    metadata_list = []

    for v in videos:
        video_id = v.get("id")
        title = v.get("title")
        ext = v.get("ext", "mp4")
        filepath = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        # Normalize to mp4
        if not filepath.endswith(".mp4"):
            mp4_path = filepath.rsplit(".", 1)[0] + ".mp4"
            subprocess.run(["ffmpeg", "-i", filepath, "-c:v", "libx264", "-c:a", "aac", mp4_path, "-y"])
            filepath = mp4_path

        metadata = {
            "id": video_id,
            "title": title,
            "filepath": filepath,
            "source": "youtube",
        }
        metadata_list.append(metadata)

    # Append to metadata.json
    existing_data = []
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            existing_data = json.load(f)

    with open(META_FILE, "w") as f:
        json.dump(existing_data + metadata_list, f, indent=2)

    print(f"✅ Downloaded {len(metadata_list)} videos. Metadata saved to {META_FILE}.")

if __name__ == "__main__":
    # Example: Trending Shorts or single short
    test_url = input("Enter YouTube Shorts URL: ")
    download_shorts(test_url)
