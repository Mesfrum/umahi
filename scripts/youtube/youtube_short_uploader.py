import os
import pickle
import requests
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

# OAuth scopes required for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.pickle"
CLIENT_SECRET = "umahi.apps.googleusercontent.com.json"  # Replace with your file

def get_authenticated_service():
    creds = None
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # Refresh or request new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save token for next time
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def download_video_from_url(video_url, output_file="temp_video.mp4", max_retries=3, timeout=30):
    """
    Download video from a given URL with retries, timeout, and graceful degradation.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Downloading video from {video_url}...")
            response = requests.get(video_url, stream=True, timeout=timeout)
            response.raise_for_status()

            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)

            print(f"✅ Video successfully downloaded to {output_file}")
            return output_file

        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout on attempt {attempt + 1}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error on attempt {attempt + 1}: {e}. Retrying...")

        attempt += 1
        time.sleep(2)  # backoff before retry

    print("❌ Failed to download video after multiple attempts. Proceeding without video.")
    return None

def upload_youtube_short(video_file, title, description, tags=None, category_id="22", privacy="public"):
    youtube = get_authenticated_service()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    media_file = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    print("Uploading video...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload Progress: {int(status.progress() * 100)}%")

    print("✅ Upload Complete")
    print("Video URL: https://youtu.be/" + response["id"])

if __name__ == "__main__":
    # === CONFIG ===
    use_remote = True  # Change to False to use local file
    video_url = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"
    local_file = "sample_short.mp4"  # Your local file
    title = "My YouTube Short via API"
    description = "This is a test YouTube Short uploaded via API."

    if use_remote:
        video_path = download_video_from_url(video_url)
    else:
        video_path = local_file

    upload_youtube_short(
        video_file=video_path,
        title=title,
        description=description,
        tags=["shorts", "api", "automation"],
        privacy="public"
    )

    # Cleanup if video was downloaded
    if use_remote and os.path.exists(video_path):
        os.remove(video_path)
        print("🧹 Temporary file deleted")
