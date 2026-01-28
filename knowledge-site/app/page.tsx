
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
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-start py-32 px-16 bg-white dark:bg-black sm:items-start">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          {/* The original h1 and p tags are replaced by the posts map */}
          {posts.map((post: any) => {
            // "Published" is a date property based on main.py analysis
            const dateStr = post.properties.Published?.date?.start;
            const date = dateStr ? new Date(dateStr).toLocaleDateString("ja-JP") : "";

            const title = post.properties.Title?.title?.[0]?.plain_text || "No Title";

            return (
              <Link
                key={post.id}
                href={`/${post.id}`}
                className="block p-6 border rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors"
              >
                <h2 className="text-2xl font-semibold mb-2 text-black dark:text-zinc-50">
                  {title}
                </h2>
                <p className="text-zinc-500 text-sm">{date}</p>
              </Link>
            );
          })}
        </div>



      </main>
    </div>
  );
}
