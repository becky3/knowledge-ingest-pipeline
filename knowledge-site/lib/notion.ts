import { Client } from "@notionhq/client";

const notionToken = process.env.NOTION_TOKEN;

if (!notionToken) {
  throw new Error("Missing NOTION_TOKEN environment variable");
}

export const notion = new Client({
  auth: notionToken,
});

export const databaseId = process.env.NOTION_DATABASE_ID;

if (!databaseId) {
  throw new Error("Missing NOTION_DATABASE_ID environment variable");
}
