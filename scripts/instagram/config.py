import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("FB_LONG_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
