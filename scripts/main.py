import feedparser
import requests
import os
import re
from html import unescape
from urllib.parse import urlsplit, urlunsplit
from notion_client import Client
from openai import OpenAI

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

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DB_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
TEST_MODE = (os.getenv("TEST_MODE") or "").lower() in ("1", "true", "yes", "y", "on")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN is not set. Put it in .env or your environment.")
if not DB_ID:
    raise RuntimeError("DB_ID is not set. Put it in .env or your environment.")

if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Put it in .env or your environment.")

notion = Client(auth=NOTION_TOKEN)
client = None if TEST_MODE else OpenAI(api_key=OPENAI_KEY)

feeds = [
 "https://medium.com/feed/towards-data-science",
 "https://medium.com/feed/tag/artificial-intelligence"
]

_DB_CONTEXT_CACHE = None

def get_database_context(database_id: str) -> dict:
    global _DB_CONTEXT_CACHE
    if _DB_CONTEXT_CACHE:
        return _DB_CONTEXT_CACHE
    try:
        db = notion.databases.retrieve(database_id=database_id)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve database. Check NOTION_TOKEN, DB_ID, and sharing permissions. ({exc})"
        ) from exc
    db_id = db.get("id")
    db_object = db.get("object")
    props = db.get("properties", {})
    data_sources = db.get("data_sources", [])
    db_url = db.get("url")
    db_title = ""
    title_items = db.get("title") or []
    if title_items:
        db_title = "".join([t.get("plain_text", "") for t in title_items])
    if not db_id:
        raise RuntimeError(
            "Failed to read database ID. DB_ID may be incorrect or the integration lacks access."
        )
    if not data_sources:
        raise RuntimeError("No data_sources found for the database. Check permissions.")
    data_source_id = data_sources[0].get("id")
    if props:
        _DB_CONTEXT_CACHE = {"db": db, "data_source_id": data_source_id}
        return _DB_CONTEXT_CACHE
    try:
        data_source = notion.data_sources.retrieve(data_source_id=data_source_id)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve data source. Check integration access. ({exc})"
        ) from exc
    ds_props = data_source.get("properties", {})
    if ds_props:
        _DB_CONTEXT_CACHE = {"db": db, "data_source_id": data_source_id}
        return _DB_CONTEXT_CACHE
    raise RuntimeError(
        "Failed to read database properties. DB_ID may be incorrect or the integration lacks access."
    )

def ensure_db_access(database_id: str) -> None:
    get_database_context(database_id)

def strip_html(html: str) -> str:
    # Simple tag stripper to avoid extra dependencies.
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
    try:
        normalized = normalize_url(url)
        raw = url
        data_source_id = get_data_source_id(database_id)
        result = notion.data_sources.query(
            **{
                "data_source_id": data_source_id,
                "filter": {"property": "URL", "url": {"equals": normalized}},
                "page_size": 1,
            }
        )
        normalized_matches = len(result.get("results", []))
        if normalized_matches > 0:
            return True

        if raw != normalized:
            result = notion.data_sources.query(
                **{
                    "data_source_id": data_source_id,
                    "filter": {"property": "URL", "url": {"equals": raw}},
                    "page_size": 1,
                }
            )
            raw_matches = len(result.get("results", []))
            return raw_matches > 0

        return False
    except Exception as exc:
        print(f"  -> Notion check error: {exc}")
        # If the check fails, allow processing rather than hard-fail.
        return False


_DATA_SOURCE_ID_CACHE = None
def get_data_source_id(database_id: str) -> str:
    global _DATA_SOURCE_ID_CACHE
    if _DATA_SOURCE_ID_CACHE:
        return _DATA_SOURCE_ID_CACHE
    context = get_database_context(database_id)
    _DATA_SOURCE_ID_CACHE = context["data_source_id"]
    return _DATA_SOURCE_ID_CACHE


all_entries = []
ensure_db_access(DB_ID)
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
    print(f"[{processed}/{total_entries}] {e.title}")
    if notion_page_exists_by_url(DB_ID, e.link):
        print("  -> skip (already exists)")
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

    prompt = f"""
    以下の記事を日本語で3行要約し、
    重要ポイントを箇条書きで出力してください。
    ---
    {article_text}
    """

    if TEST_MODE:
        print("  -> summary skipped (TEST_MODE)")
        print("  -> Notion write skipped (TEST_MODE)")
        added_count += 1  # count as would-add for parity with non-test runs
        continue

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        summary = res.choices[0].message.content

        notion.pages.create(
          parent={"type": "data_source_id", "data_source_id": get_data_source_id(DB_ID)},
          properties={
            "Title":{"title":[{"text":{"content":e.title}}]},
            "Summary":{"rich_text":[{"text":{"content":summary}}]},
            "URL":{"url":e.link}
          }
        )
        added_count += 1
        print("  -> done")
    except Exception as ex:
        print(f"  -> ERROR: Failed to process entry '{e.title}' (URL: {normalized_link}): {ex}")
        continue

print(f"Added: {added_count}, Skipped: {skipped_count}")
