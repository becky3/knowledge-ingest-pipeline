import { Client } from "@notionhq/client";

let notionClient: Client | null = null;

export const getNotionClient = () => {
  if (!notionClient) {
    const notionToken = process.env.NOTION_TOKEN;

    if (!notionToken) {
      throw new Error("Missing NOTION_TOKEN environment variable");
    }

    notionClient = new Client({
      auth: notionToken,
    });
  }
  return notionClient;
};

export const getDatabaseId = () => {
  // Support both specific and generic names for compatibility
  const databaseId = process.env.NOTION_DATABASE_ID || process.env.DB_ID;

  if (!databaseId) {
    throw new Error("Missing NOTION_DATABASE_ID or DB_ID environment variable");
  }
  return databaseId;
};

// Backwards compatibility for now, but deprecated
export const notion = new Client({ auth: process.env.NOTION_TOKEN || "dummy" }); // unsafe, removed export
