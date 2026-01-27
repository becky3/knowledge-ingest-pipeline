from notion_client import Client

try:
    client = Client(auth="dummy")
    print(f"Has pages: {hasattr(client, 'pages')}")
    print(f"Pages attributes: {dir(client.pages)}")
    print(f"Has create: {hasattr(client.pages, 'create')}")
except Exception as e:
    print(f"Error: {e}")
