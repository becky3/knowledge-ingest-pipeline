
import { getPage } from "../../lib/notion";
import { notFound } from "next/navigation";
import Link from "next/link";

export const revalidate = 60;

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
    const { slug } = await params;
    // slug is actually the pageId here
    const page = await getPage(slug);

    if (!page) {
        notFound();
    }

    // Extract valid properties
    const props = (page as any).properties;
    const title = props.Title?.title?.[0]?.plain_text || "No Title";
    const originalUrl = props.URL?.url || null;
    // Extract summary (checking for capitalization just in case, though debug confirmed 'Summary')
    const summary = props.Summary?.rich_text || props.summary?.rich_text || [];

    return (
        <div className="flex min-h-screen flex-col items-center justify-start bg-zinc-50 font-sans dark:bg-black">
            <main className="flex min-h-screen w-full max-w-3xl flex-col items-start justify-start py-12 px-6 bg-white dark:bg-black">
                <Link href="/" className="mb-8 text-zinc-500 hover:text-black dark:hover:text-white transition-colors">
                    ← Back to Home
                </Link>

                <article className="w-full">
                    <h1 className="text-4xl font-bold mb-4 text-black dark:text-zinc-50">
                        {title}
                    </h1>

                    {originalUrl && (
                        <div className="mb-8">
                            <a
                                href={originalUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline break-all"
                            >
                                {originalUrl}
                            </a>
                        </div>
                    )}

                    <div className="flex flex-col gap-4 text-black dark:text-zinc-200 leading-relaxed text-lg">
                        {/* Render Summary if available */}
                        {summary.length > 0 ? (
                            <div className="mb-8 p-4 bg-zinc-100 dark:bg-zinc-900 rounded-lg">
                                <p>
                                    {summary.map((text: any) => text.plain_text).join("")}
                                </p>
                            </div>
                        ) : (
                            <p className="text-zinc-500 italic">No content available for this article.</p>
                        )}
                    </div>
                </article>
            </main>
        </div>
    );
}
