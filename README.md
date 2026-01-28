# knowledge-ingest-pipeline

RSS から記事を取得し、要約して Notion に保存するスクリプトです。
ローカル実行と GitHub Actions の両方で動く前提になっています。

## 概要

- RSS を読み込み（現在は Medium のフィードを2件）
- 既存の Notion ページを URL で重複チェック
- OpenAI で日本語要約を作成
- Notion にページを追加

## 必要要件

- Python 3.10+
- uv

## セットアップ

1) 依存関係をインストール

```bash
uv sync
```

2) `.env` を作成

`.env.example` をコピーして値を入れてください。

必要な環境変数:

- `NOTION_TOKEN`: Notion Integration のトークン
- `NOTION_DATABASE_ID`: Notion データベース ID
- `OPENAI_API_KEY` または `OPENAI_KEY`: OpenAI の API キー
- `TEST_MODE` (任意): `true` の場合は書き込みをスキップ

## Notion データベース設定

連携する Notion データベースには以下のプロパティが必要です。

| プロパティ名 | 種類 (Type) | 説明 |
| --- | --- | --- |
| **Title** | Title (タイトル) | 記事のタイトル |
| **URL** | URL | 記事のオリジナルの URL |
| **Summary** | Text (テキスト) | AI による要約本文 |
| **Published** | Date (日付) | 記事の発行日 (ソートに使用) |


## 実行

```bash
uv run python scripts/main.py
```

## 動作のポイント

- `.env` の値は **常に優先** されます。
- 既存チェックは URL を正規化して比較します（クエリやフラグメントは除外）。
- Notion への保存は **生の URL** を使用します。

## トラブルシュート

- `ModuleNotFoundError` が出る場合は `uv sync` を実行してください。
- Notion の権限エラーが出る場合は Integration の共有と `NOTION_DATABASE_ID` を確認してください。
