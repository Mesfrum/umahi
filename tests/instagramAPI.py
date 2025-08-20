import os
import time
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Config
ACCESS_TOKEN = os.getenv("FB_LONG_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Pahalgam_Valley.jpg/1200px-Pahalgam_Valley.jpg"
CAPTION = "#AutomatedPost"


def validate_token():
    print("🔐 Validating access token...")
    url = "https://graph.facebook.com/me"
    try:
        response = requests.get(url, params={"access_token": ACCESS_TOKEN})
        response.raise_for_status()
        print(f"✅ Token valid. User: {response.json().get('name', 'Unknown')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Token validation failed: {e}")
        return False


def validate_instagram_account():
    print("📱 Validating Instagram Business account...")
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}"
    fields = "username,name,biography,followers_count,media_count"

    try:
        response = requests.get(
            url, params={"fields": fields, "access_token": ACCESS_TOKEN}
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ @{data.get('username')} ({data.get('followers_count')} followers)")

        # Check media access
        media_check = requests.get(
            f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
            params={"access_token": ACCESS_TOKEN, "limit": 1},
        )
        if media_check.ok:
            print("✅ Media access confirmed.")
            return True
        else:
            print("⚠️ Cannot access media endpoint. Ensure account is Business/Creator.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ IG account validation failed: {e}")
        return False


def check_image_url():
    print("🖼️ Verifying image URL...")
    try:
        resp = requests.head(IMAGE_URL, timeout=10)
        content_type = resp.headers.get("Content-Type", "Unknown")
        if resp.ok and content_type.startswith("image/"):
            print(f"✅ URL valid. Type: {content_type}")
            return True
        print(f"❌ Invalid image content type: {content_type}")
        return False
    except Exception as e:
        print(f"❌ URL check failed: {e}")
        return False


def create_media_container():
    print("📸 Creating media container...")
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {"image_url": IMAGE_URL, "caption": CAPTION, "access_token": ACCESS_TOKEN}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        container_id = response.json()["id"]
        print(f"✅ Media container created: {container_id}")
        return container_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create container: {e}")
        print(f"Response: {response.text}")
        return None


def publish_media(container_id):
    print("🚀 Publishing post...")
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    try:
        response = requests.post(
            url, data={"creation_id": container_id, "access_token": ACCESS_TOKEN}
        )
        response.raise_for_status()
        print(f"✅ Post published! ID: {response.json().get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Publish failed: {e}")
        print(f"Response: {response.text}")


def main():
    print("📤 Instagram Auto-Post Script")
    print("=" * 50)

    if not ACCESS_TOKEN or not IG_USER_ID:
        print("❌ ACCESS_TOKEN or IG_USER_ID missing in .env")
        return

    if not validate_token():
        return

    if not validate_instagram_account():
        return

    if not check_image_url():
        return

    container_id = create_media_container()
    if container_id:
        time.sleep(5)  # Wait before publishing
        publish_media(container_id)


if __name__ == "__main__":
    main()
