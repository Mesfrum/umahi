import time
import requests
from config import ACCESS_TOKEN, IG_USER_ID
from utils import validate_token, validate_instagram_account, is_valid_image_url

CAPTION = "#AutomatedPost"
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Pahalgam_Valley.jpg/1200px-Pahalgam_Valley.jpg"


def create_photo_container():
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {"image_url": IMAGE_URL, "caption": CAPTION, "access_token": ACCESS_TOKEN}
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()["id"]


def publish_media(container_id):
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    r = requests.post(
        url, data={"creation_id": container_id, "access_token": ACCESS_TOKEN}
    )
    r.raise_for_status()
    print(f"✅ Image post published! ID: {r.json().get('id')}")


def main():
    print("📤 Instagram Image Upload Script")
    if not (validate_token() and validate_instagram_account()):
        return

    if not is_valid_image_url(IMAGE_URL):
        print("❌ Invalid image URL.")
        return

    container_id = create_photo_container()
    time.sleep(5)
    publish_media(container_id)


if __name__ == "__main__":
    main()
