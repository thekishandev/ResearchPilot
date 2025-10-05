import { CheckCircle2, Loader2, Server, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'

interface SourceStatus {
  name: string
  displayName: string
  status: 'pending' | 'querying' | 'success' | 'error'
  responseTime?: number
  resultCount?: number
  error?: string
}

interface OrchestrationStatusProps {
  sources?: SourceStatus[]
  isActive: boolean
}

const DEFAULT_SOURCES: SourceStatus[] = [
  { name: 'web-search', displayName: 'Web Search', status: 'pending' },
  { name: 'arxiv', displayName: 'ArXiv Papers', status: 'pending' },
  { name: 'database', displayName: 'Database Cache', status: 'pending' },
  { name: 'filesystem', displayName: 'Documents', status: 'pending' },
  { name: 'github', displayName: 'GitHub Code', status: 'pending' },
  { name: 'news', displayName: 'News API', status: 'pending' },
]

export function OrchestrationStatus({ sources, isActive }: OrchestrationStatusProps) {
  const displaySources = sources || DEFAULT_SOURCES

  const getStatusIcon = (status: SourceStatus['status']) => {
    switch (status) {
      case 'querying':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Server className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (source: SourceStatus) => {
    if (source.status === 'success' && source.resultCount !== undefined) {
      return (
        <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800">
          {source.resultCount} results
        </Badge>
      )
    }
    if (source.status === 'error') {
      return (
        <Badge variant="outline" className="text-xs bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800">
          Failed
        </Badge>
      )
    }
    if (source.status === 'querying') {
      return (
        <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800">
          Querying...
        </Badge>
      )
    }
    return null
  }

  const getResponseTime = (source: SourceStatus) => {
    if (source.status === 'success' && source.responseTime) {
      return (
        <span className="text-xs text-muted-foreground ml-2">
          {source.responseTime}ms
        </span>
      )
    }
    return null
  }

  if (!isActive) {
    return null
  }

  const successCount = displaySources.filter(s => s.status === 'success').length
  const totalCount = displaySources.length

  return (
    <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 dark:border-blue-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Server className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            Live Orchestration
          </CardTitle>
          <Badge variant="outline" className="bg-white/50 dark:bg-slate-900/50">
            {successCount}/{totalCount} sources
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displaySources.map((source) => (
            <div
              key={source.name}
              className="flex items-center justify-between p-3 rounded-lg bg-white/60 dark:bg-slate-900/60 backdrop-blur-sm transition-all duration-300 hover:bg-white/80 dark:hover:bg-slate-900/80"
            >
              <div className="flex items-center gap-3 flex-1">
                {getStatusIcon(source.status)}
                <div className="flex-1">
                  <div className="font-medium text-sm">{source.displayName}</div>
                  {source.error && (
                    <div className="text-xs text-red-600 dark:text-red-400 mt-0.5">
                      {source.error}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getResponseTime(source)}
                {getStatusBadge(source)}
              </div>
            </div>
          ))}
        </div>

        {/* Progress Summary */}
        {successCount > 0 && (
          <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium text-blue-700 dark:text-blue-300">
                {Math.round((successCount / totalCount) * 100)}% complete
              </span>
            </div>
            <div className="mt-2 h-2 bg-blue-100 dark:bg-blue-900 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500 ease-out"
                style={{ width: `${(successCount / totalCount) * 100}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
