import { useState } from 'react'
import { Search, Loader2, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { submitResearch } from '@/lib/api'
import { ResearchQuery, ResearchStatus } from '@/types/research'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { SourcesPanel } from './SourcesPanel'
import { ResultsDisplay } from './ResultsDisplay'

export function ResearchInterface() {
  const [query, setQuery] = useState('')
  const [researchStatus, setResearchStatus] = useState<ResearchStatus | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)

  const mutation = useMutation({
    mutationFn: (data: ResearchQuery) => submitResearch(data),
    onSuccess: (response) => {
      console.log('Research submitted:', response)
      // Set initial status
      setResearchStatus({
        id: response.id,
        status: response.status || 'processing',
        query: query.trim(),
      } as ResearchStatus)
      // Start streaming results
      startStreamingResults(response.id)
    },
    onError: (error) => {
      console.error('Research submission error:', error)
    },
  })

  const startStreamingResults = async (researchId: string) => {
    setIsStreaming(true)
    console.log(`Starting SSE stream for research ${researchId}`)
    
    try {
      const eventSource = new EventSource(`/api/v1/research/stream/${researchId}`)
      
      let messageCount = 0
      
      eventSource.onopen = () => {
        console.log('SSE connection opened')
      }
      
      eventSource.onmessage = (event) => {
        try {
          messageCount++
          console.log(`SSE message #${messageCount} received, length: ${event.data.length}`)
          console.log('SSE message preview:', event.data.substring(0, 200))
          
          const data = JSON.parse(event.data)
          console.log('Parsed SSE data status:', data.status)
          
          // Ensure we have a valid status object
          if (data && typeof data === 'object' && data.status) {
            setResearchStatus(data)
            console.log(`Updated research status to: ${data.status}`)
            
            // Close the connection on completion or failure
            if (data.status === 'completed' || data.status === 'failed') {
              console.log(`Research ${data.status}, closing SSE connection after ${messageCount} messages`)
              eventSource.close()
              setIsStreaming(false)
            }
          } else {
            console.warn('Invalid SSE data format:', data)
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error)
          console.error('Raw data that failed to parse:', event.data)
        }
      }
      
      eventSource.onerror = (error) => {
        console.error('SSE error event:', error)
        console.error('EventSource readyState:', eventSource.readyState)
        
        // ReadyState: 0=CONNECTING, 1=OPEN, 2=CLOSED
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('SSE connection closed by server')
        }
        
        eventSource.close()
        setIsStreaming(false)
      }
    } catch (error) {
      console.error('Error creating EventSource:', error)
      setIsStreaming(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    console.log('Submit clicked, query length:', query.length)
    
    if (!query.trim() || query.length < 10) {
      console.log('Query too short, minimum 10 characters required')
      return
    }

    setResearchStatus(null)
    
    console.log('Submitting research query:', query)
    mutation.mutate({
      query: query.trim(),
      sources: undefined,
      max_sources: 6,
      include_credibility: true,
    })
  }

  const getStatusIcon = () => {
    if (!researchStatus) return null
    
    switch (researchStatus.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
    }
  }

  const isLoading = mutation.isPending || isStreaming

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-8">
        <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary via-blue-600 to-purple-600 bg-clip-text text-transparent">
          Transform Hours into Seconds
        </h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          AI-powered research synthesis from 6+ data sources using ultra-fast Cerebras inference.
          Get comprehensive intelligence reports in under 10 seconds.
        </p>
      </div>

      {/* Query Input */}
      <Card>
        <CardHeader>
          <CardTitle>Research Query</CardTitle>
          <CardDescription>
            Enter your research question. We'll query web search, academic papers, GitHub, news, and more.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="Example: What are the latest breakthroughs in quantum computing?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-h-[120px] resize-none"
              disabled={isLoading}
            />
            
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                {query.length} / 1000 characters
                {query.length > 0 && query.length < 10 && (
                  <span className="text-amber-600 dark:text-amber-400 ml-2">
                    • Minimum 10 characters required
                  </span>
                )}
              </div>
              
              <Button
                type="submit"
                disabled={isLoading || query.length < 10}
                className="min-w-[200px]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Researching...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Start Research
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Status Card */}
      {researchStatus && researchStatus.status && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStatusIcon()}
                <div>
                  <div className="font-medium">
                    Status: {researchStatus.status.charAt(0).toUpperCase() + researchStatus.status.slice(1)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {researchStatus.status === 'processing' && 'Querying sources and synthesizing results...'}
                    {researchStatus.status === 'completed' && 'Research completed successfully'}
                    {researchStatus.status === 'failed' && 'Research failed. Please try again.'}
                  </div>
                </div>
              </div>
              
              {researchStatus.credibility_score !== undefined && (
                <Badge variant={researchStatus.credibility_score >= 0.7 ? 'default' : 'secondary'}>
                  Credibility: {(researchStatus.credibility_score * 100).toFixed(0)}%
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Sources Panel */}
      {researchStatus?.results && (
        <SourcesPanel results={researchStatus.results} />
      )}

      {/* Results Display */}
      {researchStatus?.synthesis && (
        <ResultsDisplay
          synthesis={researchStatus.synthesis}
          credibilityScore={researchStatus.credibility_score}
        />
      )}

      {/* Error Display */}
      {researchStatus?.error && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <div className="font-medium text-red-900 dark:text-red-100">
                  Error
                </div>
                <div className="text-sm text-red-700 dark:text-red-300 mt-1">
                  {researchStatus.error}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
