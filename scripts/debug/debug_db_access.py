import os
import logging
from notion_client import Client
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
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_DATABASE_ID = str(uuid.UUID(NOTION_DATABASE_ID))

print(f"Checking NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")

client = Client(auth=NOTION_TOKEN)

try:
    # Try to retrieve the database
    db = client.databases.retrieve(database_id=NOTION_DATABASE_ID)
    print("Database retrieve success!")
    print(f"Title: {db.get('title')}")
except Exception as e:
    print(f"Database retrieve failed: {e}")
    if hasattr(e, "body"):
        print(f"Body: {e.body}")
    
    # If not a database, maybe it is a page?
    print("\nTrying to retrieve as Page...")
    try:
        page = client.pages.retrieve(page_id=NOTION_DATABASE_ID)
        print("Page retrieve success!")
        print(f"Page Type: {page.get('object')}")
        print(f"Page URL: {page.get('url')}")
        
        # Look for child database
        print("\nChecking for child blocks (looking for database)...")
        children = client.blocks.children.list(block_id=NOTION_DATABASE_ID)
        for block in children.get("results", []):
            if block.get("type") == "child_database":
                print(f"FOUND CHILD DATABASE!")
                print(f"ID: {block.get('id')}")
                print(f"Title: {block.get('child_database', {}).get('title')}")
            elif block.get("type") == "child_page":
                print(f"Found child page: {block.get('child_page', {}).get('title')} ({block.get('id')})")
            else:
                print(f"Found block: {block.get('type')}")
                
    except Exception as e2:
        print(f"Page retrieve failed: {e2}")

