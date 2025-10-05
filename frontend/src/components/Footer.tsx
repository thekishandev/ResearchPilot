export function Footer() {
  return (
    <footer className="border-t bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">
            <p>
              Built for <strong>FutureStack GenAI Hackathon 2024</strong>
            </p>
            <p className="text-xs mt-1">
              Powered by Cerebras, Meta Llama, and Docker MCP Gateway
            </p>
          </div>
          
          <div className="flex items-center gap-4 text-sm">
            <a
              href="/docs"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Documentation
            </a>
            <a
              href="/api/v1/health"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              API Status
            </a>
            <span className="text-muted-foreground">
              © 2024 ResearchPilot
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}
