import { Client } from "@notionhq/client";

export const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

export const databaseId = process.env.NOTION_DATABASE_ID;

if (!databaseId) {
  throw new Error("Missing NOTION_DATABASE_ID in .env.local");
}
