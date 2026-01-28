import os
import requests
import json
import uuid

def load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ[key] = value

load_dotenv(".env")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID_RAW = os.getenv("NOTION_DATABASE_ID")

try:
    NOTION_DATABASE_ID = str(uuid.UUID(NOTION_DATABASE_ID_RAW))
except ValueError:
    NOTION_DATABASE_ID = NOTION_DATABASE_ID_RAW

print(f"Testing Raw Request with ID: {NOTION_DATABASE_ID}")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
print(f"POST {url}")

try:
    resp = requests.post(url, headers=headers, json={"page_size": 1})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")
