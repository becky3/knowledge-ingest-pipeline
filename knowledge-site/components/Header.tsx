import Link from "next/link";
import { BookOpen } from "lucide-react";

export function Header() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 glass">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link
                    href="/"
                    className="flex items-center gap-2 text-xl font-bold tracking-tight hover:opacity-80 transition-opacity"
                >
                    <div className="p-1.5 bg-primary/10 rounded-lg text-primary">
                        <BookOpen className="w-5 h-5" />
                    </div>
                    <span>Curated Knowledge</span>
                </Link>

                <div className="flex items-center gap-4">
                    <a
                        href="https://github.com/becky3/knowledge-ingest-pipeline"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                    >
                        GitHub
                    </a>
                </div>
            </div>
        </header>
    );
}
