export function Footer() {
    return (
        <footer className="border-t border-border mt-auto bg-muted/30">
            <div className="container mx-auto px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
                <p>© {new Date().getFullYear()} Rhythmcan. All rights reserved.</p>
                <p>Powered by Notion & Next.js</p>
            </div>
        </footer>
    );
}
