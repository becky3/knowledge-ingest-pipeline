import os
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
client = Client(auth=NOTION_TOKEN)

try:
    print(f"Has data_sources: {hasattr(client, 'data_sources')}")
    if hasattr(client, 'data_sources'):
         print(f"Data Sources Attributes: {dir(client.data_sources)}")
except Exception as e:
    print(e)
