import time
import requests
from config import ACCESS_TOKEN, IG_USER_ID
from utils import validate_token, validate_instagram_account, is_valid_video_url

CAPTION = "#AutomatedReel"
VIDEO_URL = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"


def create_reel_container():
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "video_url": VIDEO_URL,
        "caption": CAPTION,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN,
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()["id"]


def wait_for_processing(container_id, max_attempts=10, delay=5):
    url = f"https://graph.facebook.com/v19.0/{container_id}"
    params = {"fields": "status_code", "access_token": ACCESS_TOKEN}

    print("⏳ Waiting for video processing to complete...")
    for attempt in range(max_attempts):
        response = requests.get(url, params=params)
        response.raise_for_status()
        status = response.json().get("status_code", "UNKNOWN")

        print(f"   Attempt {attempt+1}: Status = {status}")

        if status == "FINISHED":
            print("✅ Video is ready to publish.")
            return True
        elif status == "ERROR":
            print("❌ Instagram failed to process the video.")
            return False

        time.sleep(delay)

    print("❌ Timed out waiting for video to process.")
    return False


def publish_media(container_id):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    r = requests.post(
        url, data={"creation_id": container_id, "access_token": ACCESS_TOKEN}
    )
    r.raise_for_status()
    print(f"✅ Reel published! ID: {r.json().get('id')}")


def main():
    print("📤 Instagram Reel Upload Script")
    if not (validate_token() and validate_instagram_account()):
        return

    if not is_valid_video_url(VIDEO_URL):
        print("❌ Invalid video URL.")
        return

    container_id = create_reel_container()

    if wait_for_processing(container_id):
        publish_media(container_id)
    else:
        print("❌ Skipping publish due to processing failure.")


if __name__ == "__main__":
    main()
