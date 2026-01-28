
import Link from "next/link";
import { getDatabase } from "../lib/notion";

export const revalidate = 60;


export default async function Home() {
  let posts: any[] = [];
  try {
    posts = await getDatabase();
  } catch (error) {
    console.error("Failed to fetch posts:", error);
    // Continue with empty posts to avoid build failure
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-start py-16 px-6 bg-white dark:bg-black sm:items-start">
        <h1 className="text-4xl font-bold mb-12 text-black dark:text-zinc-50 tracking-tight self-start">
          Curated Knowledge
        </h1>
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left w-full">
          {/* The original h1 and p tags are replaced by the posts map */}
          {posts.map((post: any) => {
            // "Published" is a date property based on main.py analysis
            const dateStr = post.properties.Published?.date?.start;
            const date = dateStr ? new Date(dateStr).toLocaleDateString("ja-JP") : "";

            const title = post.properties.Title?.title?.[0]?.plain_text || "No Title";
            const originalUrl = post.properties.URL?.url || "#";
            const summary = post.properties.Summary?.rich_text || post.properties.summary?.rich_text || [];

            return (
              <div
                key={post.id}
                className="w-full p-6 border rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors"
              >
                <a
                  href={originalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block mb-2 group"
                >
                  <h2 className="text-2xl font-semibold text-black dark:text-zinc-50 group-hover:underline">
                    {title}
                  </h2>
                  <p className="text-zinc-500 text-sm mt-1">{date}</p>
                </a>

                {/* Summary Rendering */}
                {summary.length > 0 && (
                  <div className="text-zinc-700 dark:text-zinc-300 leading-relaxed text-sm lg:text-base">
                    <p>
                      {summary.map((text: any) => text.plain_text).join("")}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>



      </main>
    </div>
  );
}
