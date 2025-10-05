import { useQuery } from '@tanstack/react-query'
import { Clock, ChevronRight, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'

interface HistoryItem {
  id: string
  query: string
  status: string
  created_at?: string
  completed_at?: string
}

interface ResearchHistoryProps {
  onSelectQuery: (query: string, id: string) => void
}

export function ResearchHistory({ onSelectQuery }: ResearchHistoryProps) {
  const { data: history, isLoading } = useQuery<HistoryItem[]>({
    queryKey: ['research-history'],
    queryFn: async () => {
      const response = await fetch('/api/v1/research/history?limit=10')
      if (!response.ok) throw new Error('Failed to fetch history')
      return response.json()
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const formatTimeAgo = (dateString?: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (seconds < 60) return 'just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-600" />
          Recent Research
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : history && history.length > 0 ? (
          <div className="space-y-2">
            {history.map((item) => (
              <Button
                key={item.id}
                variant="ghost"
                className="w-full justify-start text-left h-auto py-3 px-3 hover:bg-accent"
                onClick={() => onSelectQuery(item.query, item.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge 
                      variant={item.status === 'completed' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {item.status}
                    </Badge>
                    {item.created_at && (
                      <span className="text-xs text-muted-foreground">
                        {formatTimeAgo(item.created_at)}
                      </span>
                    )}
                  </div>
                  <div className="text-sm line-clamp-2 text-foreground">
                    {item.query}
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0 ml-2" />
              </Button>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground text-sm">
            <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No research history yet</p>
            <p className="text-xs mt-1">Your queries will appear here</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
