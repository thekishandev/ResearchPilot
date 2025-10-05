import { CheckCircle2, XCircle, Clock, Loader2 } from 'lucide-react'
import { SourceResult } from '@/types/research'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'

interface SourcesPanelProps {
  results: SourceResult[]
}

export function SourcesPanel({ results }: SourcesPanelProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'error':
      case 'timeout':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="default">Success</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      case 'timeout':
        return <Badge variant="destructive">Timeout</Badge>
      default:
        return <Badge variant="secondary">Processing</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Data Sources ({results.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((result) => (
            <div
              key={result.source}
              className="flex items-start gap-3 p-4 rounded-lg border bg-card"
            >
              <div className="mt-1">{getStatusIcon(result.status)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <div className="font-medium capitalize truncate">
                    {result.source.replace('-', ' ')}
                  </div>
                  {getStatusBadge(result.status)}
                </div>
                {result.response_time && (
                  <div className="text-xs text-muted-foreground">
                    {(result.response_time * 1000).toFixed(0)}ms
                  </div>
                )}
                {result.error && (
                  <div className="text-xs text-red-500 mt-1 truncate">
                    {result.error}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
