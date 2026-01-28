
import { getDatabase } from "../lib/notion";
import { ArticleCard } from "@/components/ArticleCard";

interface NotionPost {
  id: string;
  properties: {
    Title?: { title: Array<{ plain_text: string }> };
    Published?: { date: { start: string } };
    URL?: { url: string };
    Summary?: { rich_text: Array<{ plain_text: string }> };
  };
}
export default async function Home() {
  let posts: NotionPost[] = [];
  try {
    const dbPosts = await getDatabase();
    posts = dbPosts as unknown as NotionPost[];
  } catch (error) {
    console.error("Failed to fetch posts:", error);
    // Continue with empty posts to avoid build failure
  }

  return (
    <div className="flex-1 w-full bg-background">
      <section className="container mx-auto px-4 py-12 md:py-20 max-w-7xl">
        <div className="flex flex-col gap-2 mb-12 sm:mb-16">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground text-balance">
            Curated Knowledge
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl text-balance">
            Discover insights, tutorials, and articles curated from across the web.
          </p>
        </div>

        {posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-border rounded-xl bg-card/50">
            <p className="text-muted-foreground text-lg">No posts available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {posts.map((post) => {
              const dateStr = post.properties.Published?.date?.start;
              const date = dateStr
                ? new Date(dateStr).toLocaleDateString("ja-JP", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })
                : "Unknown Date";

              const title =
                post.properties.Title?.title?.[0]?.plain_text || "No Title";
              const originalUrl = post.properties.URL?.url || "#";
              const summary =
                post.properties.Summary?.rich_text
                  ?.map((t: { plain_text: string }) => t.plain_text)
                  .join("") || "";

              return (
                <ArticleCard
                  key={post.id}
                  title={title}
                  summary={summary}
                  date={date}
                  url={originalUrl}
                />
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
