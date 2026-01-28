import feedparser
import requests
import os
import re
import logging
import json
import uuid
from datetime import datetime
from time import mktime
from html import unescape
from urllib.parse import urlsplit, urlunsplit
from notion_client import Client
from openai import OpenAI
from bs4 import BeautifulSoup

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

# Works locally with .env and in GitHub Actions via secrets/env.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# Suppress noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID_RAW = os.getenv("NOTION_DATABASE_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
TEST_MODE = (os.getenv("TEST_MODE") or "").lower() in ("1", "true", "yes", "y", "on")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN is not set. Put it in .env or your environment.")

if not NOTION_DATABASE_ID_RAW:
    raise RuntimeError("NOTION_DATABASE_ID is not set. Put it in .env or your environment.")

# Format NOTION_DATABASE_ID to ensure it has dashes (required for some API endpoints/URLs)
try:
    NOTION_DATABASE_ID = str(uuid.UUID(NOTION_DATABASE_ID_RAW))
except ValueError:
    logger.warning(f"NOTION_DATABASE_ID {NOTION_DATABASE_ID_RAW} doesn't look like a UUID. Using as-is.")
    NOTION_DATABASE_ID = NOTION_DATABASE_ID_RAW

if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Put it in .env or your environment.")

notion = Client(auth=NOTION_TOKEN)
client = None if TEST_MODE else OpenAI(api_key=OPENAI_KEY)

# Load feeds from feeds.json
try:
    with open(os.path.join(os.path.dirname(__file__), "..", "feeds.json"), "r", encoding="utf-8") as f:
        feeds = json.load(f)
except Exception as e:
    logger.error(f"Failed to load feeds.json: {e}")
    feeds = []


def strip_html(html: str) -> str:
    # Use BeautifulSoup depending on availability
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception:
        # Fallback to simple regex if BS4 fails
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text


def normalize_url(url: str) -> str:
    # Drop query and fragment to avoid duplication due to tracking params.
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def notion_page_exists_by_url(database_id: str, url: str) -> bool:
    if not database_id or not url:
        return False
    
    # Use raw requests because notion-client is broken in this environment
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Ensure ID has dashes for the URL
    try:
        dashed_id = str(uuid.UUID(database_id))
    except ValueError:
        dashed_id = database_id
        
    api_url = f"https://api.notion.com/v1/databases/{dashed_id}/query"

    try:
        normalized = normalize_url(url)
        raw = url
        
        # Check normalized URL
        resp = requests.post(
            api_url, 
            headers=headers, 
            json={
                "filter": {"property": "URL", "url": {"equals": normalized}},
                "page_size": 1,
            },
            timeout=10
        )
        if resp.status_code == 200 and resp.json().get("results"):
            return True
            
        # Check raw URL if different
        if raw != normalized:
            resp = requests.post(
                api_url, 
                headers=headers, 
                json={
                    "filter": {"property": "URL", "url": {"equals": raw}},
                    "page_size": 1,
                },
                timeout=10
            )
            if resp.status_code == 200 and resp.json().get("results"):
                return True
            
        return False
    except Exception as exc:
        logger.warning(f"Notion check error: {exc}")
        return False


all_entries = []

for url in feeds:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries[:5])

total_entries = len(all_entries)
processed = 0
added_count = 0
skipped_count = 0

for e in all_entries:
    processed += 1
    normalized_link = normalize_url(e.link)
    logger.info(f"[{processed}/{total_entries}] {e.title}")
    if notion_page_exists_by_url(NOTION_DATABASE_ID, e.link):
        logger.info("  -> skip (already exists)")
        skipped_count += 1
        continue

    # Prefer RSS-provided content/summary to avoid heavy HTML parsing libs.
    raw_html = ""
    if "content" in e and e.content:
        raw_html = e.content[0].value
    elif "summary" in e and e.summary:
        raw_html = e.summary
    else:
        try:
            resp = requests.get(e.link, timeout=15)
            resp.raise_for_status()
            raw_html = resp.text
        except requests.RequestException:
            raw_html = ""

    article_text = strip_html(raw_html)[:6000]

    # Date parsing
    published_date_str = None
    if "published_parsed" in e and e.published_parsed:
        try:
            dt = datetime.fromtimestamp(mktime(e.published_parsed))
            # Notion wants ISO8601
            published_date_str = dt.isoformat()
        except Exception:
            pass
    elif "updated_parsed" in e and e.updated_parsed:
        try:
            dt = datetime.fromtimestamp(mktime(e.updated_parsed))
            published_date_str = dt.isoformat()
        except Exception:
            pass

    # Updated Prompt Logic: Handle empty text
    content_part = f"本文:\n{article_text}" if article_text and len(article_text) > 50 else "本文: (内容が取得できませんでした。タイトルから内容を推測してください)"

    prompt = f"""
    以下の記事を日本語で3行要約し、
    重要ポイントを箇条書きで出力してください。
    もし本文がない場合は、タイトルから内容を推測して要約を作成してください。
    絶対に「情報不足で要約できない」とは答えず、推測できる範囲で出力すること。

    タイトル: {e.title}

    {content_part}
    """

    if TEST_MODE:
        logger.info("  -> summary skipped (TEST_MODE)")
        logger.info("  -> Notion write skipped (TEST_MODE)")
        added_count += 1  # count as would-add for parity with non-test runs
        continue

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        summary = res.choices[0].message.content

        properties = {
            "Title":{"title":[{"text":{"content":e.title}}]},
            "Summary":{"rich_text":[{"text":{"content":summary}}]},
            "URL":{"url":e.link}
        }
        
        if published_date_str:
            properties["Published"] = {"date": {"start": published_date_str}}

        notion.pages.create(
          parent={"database_id": NOTION_DATABASE_ID},
          properties=properties
        )
        added_count += 1
        logger.info("  -> done")
    except Exception as ex:
        logger.error(f"Failed to process entry '{e.title}' (URL: {normalized_link}): {ex}")
        continue

logger.info(f"Added: {added_count}, Skipped: {skipped_count}")
