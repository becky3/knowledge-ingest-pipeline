import os
import notion_client
from notion_client import Client
import logging

logging.basicConfig(level=logging.INFO)

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
DB_ID = os.getenv("DB_ID") # Should be the child database ID now

client = Client(auth=NOTION_TOKEN)

print(f"Testing query on DB ID: {DB_ID}")

# Try retrieve first
print("Calling Retrieve...")
try:
    db = client.databases.retrieve(database_id=DB_ID)
    print("Retrieve Success!")
    print(f"Title: {db.get('title')}")
except Exception as e:
    print(f"Retrieve Failed: {e}")


# Try direct request workaround first as main.py does
path = f"databases/{DB_ID}/query"
print(f"Calling POST {path}")
try:
    resp = client.request(
        path=path,
        method="POST",
        body={
            "page_size": 1
        }
    )
    print("Success!")
    print(resp)
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, "body"):
        print(f"Body: {e.body}")
