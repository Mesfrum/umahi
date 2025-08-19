import os
import requests
import time
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Load from environment or hardcode for test
ACCESS_TOKEN = os.getenv("FB_LONG_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Shiva_shrine%2C_Gangabal_Lake.jpg/960px-Shiva_shrine%2C_Gangabal_Lake.jpg"
CAPTION = "🎉 Hello! #AutomatedPost"


def validate_access_token(access_token):
    """Validate the access token and get user info"""
    print("🔐 Validating access token...")
    url = f"https://graph.facebook.com/me"
    params = {"access_token": access_token}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        user_info = response.json()
        print(f"✅ Token valid. User: {user_info.get('name', 'Unknown')}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"❌ Token validation failed: {e}")
        print(f"Response: {response.text}")
        return False


def find_instagram_business_accounts(access_token):
    """Find all Instagram Business accounts connected to your Facebook pages"""
    print("🔍 Searching for Instagram Business accounts...")

    # Get Facebook pages
    pages_url = "https://graph.facebook.com/v19.0/me/accounts"
    pages_params = {
        "access_token": access_token,
        "fields": "name,instagram_business_account{id,username,name,biography,followers_count}",
    }

    try:
        response = requests.get(pages_url, params=pages_params)
        response.raise_for_status()
        pages_data = response.json()

        instagram_accounts = []

        for page in pages_data.get("data", []):
            if "instagram_business_account" in page:
                ig_account = page["instagram_business_account"]
                instagram_accounts.append(
                    {
                        "page_name": page.get("name"),
                        "ig_id": ig_account.get("id"),
                        "ig_username": ig_account.get("username"),
                        "ig_name": ig_account.get("name"),
                        "ig_followers": ig_account.get("followers_count"),
                    }
                )

        if instagram_accounts:
            print(f"✅ Found {len(instagram_accounts)} Instagram Business account(s):")
            for i, account in enumerate(instagram_accounts, 1):
                print(f"   {i}. @{account['ig_username']} (ID: {account['ig_id']})")
                print(f"      Name: {account['ig_name']}")
                print(f"      Followers: {account['ig_followers']}")
                print(f"      Connected to page: {account['page_name']}")
                print()

            return instagram_accounts
        else:
            print("❌ No Instagram Business accounts found!")
            print("   Make sure you have:")
            print("   1. A Facebook Page")
            print("   2. An Instagram Business account connected to that page")
            print("   3. Admin access to both")
            return []

    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to find Instagram accounts: {e}")
        print(f"Response: {response.text}")
        return []


def validate_instagram_account(ig_user_id, access_token):
    """Validate Instagram Business Account"""
    print("📱 Validating Instagram account...")
    url = f"https://graph.facebook.com/v19.0/{ig_user_id}"

    # Try with basic fields first
    params = {
        "fields": "username,name,biography,followers_count,media_count",
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        account_info = response.json()
        print(f"✅ Instagram account found:")
        print(f"   Username: @{account_info.get('username', 'Unknown')}")
        print(f"   Name: {account_info.get('name', 'Unknown')}")
        print(f"   Followers: {account_info.get('followers_count', 'Unknown')}")
        print(f"   Media Count: {account_info.get('media_count', 'Unknown')}")

        # Test if we can access media endpoint (this requires Business account)
        media_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        media_params = {"access_token": access_token, "limit": 1}
        media_response = requests.get(media_url, params=media_params)

        if media_response.status_code == 200:
            print("✅ Account can access media endpoint (likely Business/Creator)")
            return True
        else:
            print(
                "⚠️  Cannot access media endpoint - might not be Business/Creator account"
            )
            print(f"   Media endpoint response: {media_response.text}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"❌ Instagram account validation failed: {e}")
        print(f"Response: {response.text}")
        return False


def check_image_url(image_url):
    """Check if the image URL is accessible"""
    print("🖼️ Checking image URL...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.head(image_url, timeout=10, headers=headers)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "Unknown")
        print(f"✅ Image URL accessible. Content-Type: {content_type}")
        return content_type.startswith("image/")
    except Exception as e:
        print(f"❌ Image URL check failed: {e}")
        return False


def create_media_container(ig_user_id, image_url, caption, access_token):
    """Create media container with detailed error handling"""
    print("📸 Creating media container...")
    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    params = {"image_url": image_url, "caption": caption, "access_token": access_token}

    print(f"Request URL: {url}")
    print(
        f"Request params: {json.dumps({k: v for k, v in params.items() if k != 'access_token'}, indent=2)}"
    )

    try:
        response = requests.post(url, data=params)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")

        response.raise_for_status()
        return response.json()["id"]
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        try:
            error_details = response.json()
            print(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"Raw response: {response.text}")
        raise


def publish_media(ig_user_id, creation_id, access_token):
    """Publish media with error handling"""
    print("🚀 Publishing media...")
    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    params = {"creation_id": creation_id, "access_token": access_token}

    try:
        response = requests.post(url, data=params)
        print(f"Publish response status: {response.status_code}")
        print(f"Publish response: {response.text}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Publish error: {e}")
        try:
            error_details = response.json()
            print(f"Publish error details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"Raw publish response: {response.text}")
        raise


def main():
    print("🔍 Instagram API Debugging Script")
    print("=" * 50)

    # Check required variables
    if not ACCESS_TOKEN:
        print("❌ ACCESS_TOKEN not set properly", ACCESS_TOKEN)
        return

    # Step-by-step validation
    if not validate_access_token(ACCESS_TOKEN):
        return

    # Find Instagram Business accounts first
    print("\n" + "=" * 30)
    instagram_accounts = find_instagram_business_accounts(ACCESS_TOKEN)

    if instagram_accounts:
        print("💡 Use one of these Instagram IDs in your IG_USER_ID variable:")
        for account in instagram_accounts:
            print(f"   IG_USER_ID={account['ig_id']}  # @{account['ig_username']}")
        print()

    if not IG_USER_ID:
        print("❌ IG_USER_ID not set - use one of the IDs above")
        return

    print(f"Using Instagram User ID: {IG_USER_ID}")
    print(f"Using Image URL: {IMAGE_URL}")
    print("\n" + "=" * 30)

    if not validate_instagram_account(IG_USER_ID, ACCESS_TOKEN):
        return

    if not check_image_url(IMAGE_URL):
        return

    try:
        # Create media container
        creation_id = create_media_container(
            IG_USER_ID, IMAGE_URL, CAPTION, ACCESS_TOKEN
        )
        print(f"✅ Media container created: {creation_id}")

        # Wait before publishing
        print("⏳ Waiting 5 seconds before publishing...")
        time.sleep(5)

        # Publish media
        result = publish_media(IG_USER_ID, creation_id, ACCESS_TOKEN)
        print("✅ Post published successfully!")
        print(f"Result: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"❌ Script failed: {e}")


if __name__ == "__main__":
    main()
