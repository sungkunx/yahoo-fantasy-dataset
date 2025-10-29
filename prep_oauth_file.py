# prep_oauth_file.py
import os, json
from dotenv import load_dotenv
load_dotenv()

data = {
    "consumer_key":    os.getenv("YAHOO_CLIENT_ID"),
    "consumer_secret": os.getenv("YAHOO_CLIENT_SECRET")
}
with open("oauth2.json", "w") as f:
    json.dump(data, f)
print("✅ oauth2.json(키만) 생성 완료")
