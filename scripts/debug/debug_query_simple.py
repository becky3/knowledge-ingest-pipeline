import os
import notion_client
from notion_client import Client
import logging
import uuid

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
NOTION_DATABASE_ID_RAW = os.getenv("NOTION_DATABASE_ID")

try:
    NOTION_DATABASE_ID = str(uuid.UUID(NOTION_DATABASE_ID_RAW))
    DASHED_ID = NOTION_DATABASE_ID
except ValueError:
    DASHED_ID = NOTION_DATABASE_ID_RAW

# For testing, also try non-dashed if available
NO_DASH_ID = NOTION_DATABASE_ID_RAW.replace("-", "")

client = Client(auth=NOTION_TOKEN)

def try_query(db_id, label):
    print(f"\n--- Testing Query with {label} ID: {db_id} ---")
    try:
        # Simple query without filter first
        path = f"databases/{db_id}/query"
        print(f"POST {path}")
        resp = client.request(path=path, method="POST", body={"page_size": 1})
        print("Success (No Filter)!")
        print(f"Results count: {len(resp.get('results', []))}")
        
        # Now try with filter
        print("Testing with Filter...")
        resp = client.request(
            path=path,
            method="POST",
            body={
                "filter": {"property": "URL", "url": {"equals": "https://example.com"}},
                "page_size": 1
            }
        )
        print("Success (With Filter)!")
    except Exception as e:
        print(f"Failed: {e}")
        if hasattr(e, "body"):
            print(f"Body: {e.body}")

try_query(DASHED_ID, "Dashed")
if DASHED_ID != NO_DASH_ID:
    try_query(NO_DASH_ID, "No-Dash")
