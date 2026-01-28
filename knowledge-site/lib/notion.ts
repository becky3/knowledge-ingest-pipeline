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
  const databaseId = process.env.NOTION_DATABASE_ID;

  if (!databaseId) {
    throw new Error("Missing NOTION_DATABASE_ID environment variable");
  }
  return databaseId;
};


export const getDatabase = async () => {
  const notion = getNotionClient();
  const databaseId = getDatabaseId();

  // Step 1: Specific to Notion API 2025-09-03 (SDK v5+)
  // Retrieve the database container to find the active Data Source ID
  const db = await notion.databases.retrieve({ database_id: databaseId });

  // Cast to any because data_sources might be missing from strict typedefs in some versions
  const dataSources = (db as any).data_sources;

  if (!dataSources || dataSources.length === 0) {
    throw new Error("No data sources found in the specified database. Please verify the Database ID.");
  }

  const dataSourceId = dataSources[0].id;

  // Step 2: Query using the retrieved Data Source ID
  const response = await notion.dataSources.query({
    data_source_id: dataSourceId,
    sorts: [
      {
        property: "Published",
        direction: "descending",
      },
    ],
  });

  return response.results;
};

export const getPage = async (pageId: string) => {
  const notion = getNotionClient();

  try {
    const response = await notion.pages.retrieve({ page_id: pageId });
    return response;
  } catch (error) {
    console.error("Failed to retrieve Notion page", { pageId, error });
    return null;
  }
};

