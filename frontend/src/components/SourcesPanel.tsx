import { CheckCircle2, XCircle, Clock, Loader2, Award, Shield } from 'lucide-react'
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
        return <Badge variant="default" className="bg-green-600">Success</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
      case 'timeout':
        return <Badge variant="destructive">Timeout</Badge>
      default:
        return <Badge variant="secondary">Processing</Badge>
    }
  }

  const getCredibilityScore = (source: string, status: string): number => {
    // Generate credibility scores based on source type and status
    if (status !== 'success') return 0
    
    const baseScores: Record<string, number> = {
      'arxiv': 95,
      'database': 90,
      'github': 85,
      'news': 80,
      'web-search': 75,
      'filesystem': 85
    }
    
    return baseScores[source] || 75
  }

  const getCredibilityBadge = (score: number) => {
    if (score >= 90) {
      return (
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300 dark:bg-green-950 dark:text-green-300">
          <Shield className="h-3 w-3 mr-1" />
          {score}% High Trust
        </Badge>
      )
    } else if (score >= 75) {
      return (
        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300 dark:bg-blue-950 dark:text-blue-300">
          <Award className="h-3 w-3 mr-1" />
          {score}% Verified
        </Badge>
      )
    } else if (score > 0) {
      return (
        <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300 dark:bg-yellow-950 dark:text-yellow-300">
          {score}% Moderate
        </Badge>
      )
    }
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-600" />
          Data Sources ({results.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((result) => {
            const credibilityScore = getCredibilityScore(result.source, result.status)
            
            return (
              <div
                key={result.source}
                className="flex flex-col gap-3 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start gap-3">
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
                        Response: {(result.response_time * 1000).toFixed(0)}ms
                      </div>
                    )}
                    {result.error && (
                      <div className="text-xs text-red-500 mt-1 line-clamp-2">
                        {result.error}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Credibility Score */}
                {credibilityScore > 0 && (
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="text-xs text-muted-foreground">Credibility</span>
                    {getCredibilityBadge(credibilityScore)}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
