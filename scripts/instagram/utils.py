import requests
from config import ACCESS_TOKEN, IG_USER_ID


def validate_token():
    print("🔐 Validating access token...")
    try:
        r = requests.get(
            "https://graph.facebook.com/me", params={"access_token": ACCESS_TOKEN}
        )
        r.raise_for_status()
        print(f"✅ Token valid. User: {r.json().get('name', 'Unknown')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Token validation failed: {e}")
        return False


def validate_instagram_account():
    print("📱 Validating Instagram Business account...")
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}"
    try:
        r = requests.get(
            url,
            params={
                "fields": "username,name,biography,followers_count,media_count",
                "access_token": ACCESS_TOKEN,
            },
        )
        r.raise_for_status()
        data = r.json()
        print(f"✅ @{data.get('username')} ({data.get('followers_count')} followers)")

        media_check = requests.get(
            f"{url}/media", params={"access_token": ACCESS_TOKEN, "limit": 1}
        )
        if media_check.ok:
            print("✅ Media access confirmed.")
            return True
        print("⚠️ Media access failed. Ensure account is Business/Creator.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ IG account validation failed: {e}")
        return False


def is_valid_image_url(url):
    try:
        r = requests.head(url, timeout=10)
        content_type = r.headers.get("Content-Type", "Unknown")
        return r.ok and content_type.startswith("image/")
    except Exception as e:
        print(f"❌ URL check failed: {e}")
        return False


def is_valid_video_url(url):
    try:
        r = requests.head(url, timeout=20)
        content_type = r.headers.get("Content-Type", "Unknown")
        return r.ok and content_type.startswith("video/")
    except Exception as e:
        print(f"❌ Video URL check failed: {e}")
        return False
