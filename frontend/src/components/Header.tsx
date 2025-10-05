import { Rocket, Github, Zap, Brain, Container } from 'lucide-react'
import { Badge } from './ui/badge'

export function Header() {
  return (
    <header className="border-b bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-primary rounded-lg p-2">
              <Rocket className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                ResearchPilot
              </h1>
              <p className="text-xs text-muted-foreground">
                AI Research Copilot - FutureStack GenAI Hackathon
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 flex-wrap">
            {/* Sponsor Badges */}
            <div className="hidden lg:flex items-center gap-2">
              <Badge variant="outline" className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950 dark:to-red-950 border-orange-200 dark:border-orange-800">
                <Zap className="h-3.5 w-3.5 text-orange-600 dark:text-orange-400" />
                <span className="text-xs font-medium text-orange-700 dark:text-orange-300">Powered by Cerebras</span>
              </Badge>
              
              <Badge variant="outline" className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 border-blue-200 dark:border-blue-800">
                <Brain className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" />
                <span className="text-xs font-medium text-blue-700 dark:text-blue-300">Meta Llama 3.3 70B</span>
              </Badge>
              
              <Badge variant="outline" className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950 dark:to-blue-950 border-cyan-200 dark:border-cyan-800">
                <Container className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                <span className="text-xs font-medium text-cyan-700 dark:text-cyan-300">Docker Orchestration</span>
              </Badge>
            </div>
            
            {/* Mobile: Single status badge */}
            <div className="lg:hidden flex items-center gap-1.5">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-muted-foreground">6 sources active</span>
            </div>
            
            <a
              href="https://github.com/thekishandev/ResearchPilot"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              <Github className="h-4 w-4" />
              <span className="hidden md:inline">GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </header>
  )
}
