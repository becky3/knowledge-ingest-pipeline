import { Calendar, ExternalLink, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface ArticleCardProps {
    title: string;
    summary: string;
    date: string;
    url: string;
    className?: string;
}

export function ArticleCard({ title, summary, date, url, className }: ArticleCardProps) {
    return (
        <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
                "group relative flex flex-col p-6 rounded-2xl border border-border bg-card transition-all duration-300",
                "hover:shadow-lg hover:shadow-primary/5 hover:-translate-y-1 hover:border-primary/20",
                className
            )}
        >
            <div className="flex flex-col flex-grow gap-4">
                {/* Metadata */}
                <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5" />
                    <time dateTime={date}>{date}</time>
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold leading-tight tracking-tight text-card-foreground group-hover:text-primary transition-colors">
                    {title}
                </h3>

                {/* Summary */}
                <p className="text-sm text-muted-foreground leading-relaxed">
                    {summary}
                </p>
            </div>

            {/* Footer/Action */}
            <div className="mt-6 flex items-center justify-between pt-4 border-t border-border/50">
                <span className="text-xs font-medium text-primary opacity-0 -translate-x-2 transition-all duration-300 group-hover:opacity-100 group-hover:translate-x-0 flex items-center gap-1">
                    Read Article <ArrowRight className="w-3.5 h-3.5" />
                </span>
                <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                <span className="sr-only">(opens in new tab)</span>
            </div>
        </a>
    );
}
