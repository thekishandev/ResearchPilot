import { useState, useEffect } from 'react'
import { Search, Loader2, CheckCircle2, XCircle, AlertCircle, Sparkles, MessageSquarePlus, Mic, MicOff } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { submitResearch } from '@/lib/api'
import { ResearchQuery, ResearchStatus } from '@/types/research'
import { Button } from './ui/button'
import { Textarea } from './ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { SourcesPanel } from './SourcesPanel'
import { ResultsDisplay } from './ResultsDisplay'
import { OrchestrationStatus } from './OrchestrationStatus'

const SAMPLE_QUERIES = [
  "Latest developments in quantum computing 2024",
  "AI chip market leaders and competitive analysis",
  "Climate tech investment trends and key players",
  "Recent breakthroughs in fusion energy research",
  "State of large language models and their applications"
]

interface ResearchInterfaceProps {
  initialQuery?: string
  initialResearchId?: string
}

export function ResearchInterface({ initialQuery, initialResearchId }: ResearchInterfaceProps = {}) {
  const [query, setQuery] = useState(initialQuery || '')
  const [researchStatus, setResearchStatus] = useState<ResearchStatus | null>(null)
  const [conversationHistory, setConversationHistory] = useState<ResearchStatus[]>([])  // Track all research in conversation
  const [isStreaming, setIsStreaming] = useState(false)
  const [showOrchestration, setShowOrchestration] = useState(false)
  const [currentResearchId, setCurrentResearchId] = useState<string | null>(null)  // Track current research for follow-ups
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)

  const toggleVoiceInput = () => {
    console.log('toggleVoiceInput called, recognition:', !!recognition, 'isListening:', isListening)
    
    if (!recognition) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.')
      return
    }

    if (isListening) {
      console.log('Stopping recognition...')
      recognition.stop()
    } else {
      console.log('Starting recognition...')
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting recognition:', error)
        alert('Could not start voice recognition. Please try again.')
      }
    }
  }

  // Load research if initial ID is provided
  useEffect(() => {
    if (initialResearchId) {
      fetch(`/api/v1/research/${initialResearchId}`)
        .then(res => res.json())
        .then(data => {
          setResearchStatus(data)
          setCurrentResearchId(data.id)
          setConversationHistory([data])
        })
        .catch(err => console.error('Failed to load research:', err))
    }
    if (initialQuery) {
      setQuery(initialQuery)
    }
  }, [initialResearchId, initialQuery])

  const mutation = useMutation({
    mutationFn: (data: ResearchQuery) => submitResearch(data),
    onSuccess: (response) => {
      console.log('Research submitted:', response)
      // Set initial status
      const newResearch = {
        id: response.id,
        status: response.status || 'processing',
        query: query.trim(),
      } as ResearchStatus
      
      setResearchStatus(newResearch)
      // Add to conversation history
      setConversationHistory(prev => [...prev, newResearch])
      // Update current research ID for follow-ups
      setCurrentResearchId(response.id)
      // Show orchestration status
      setShowOrchestration(true)
      // Start streaming results
      startStreamingResults(response.id)
    },
    onError: (error) => {
      console.error('Research submission error:', error)
    },
  })

  // Initialize Web Speech API after mutation is defined
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = false
      recognitionInstance.lang = 'en-US'

      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        console.log('Voice input transcript:', transcript)
        setQuery(transcript)
        setIsListening(false)
        
        // Auto-submit the query after voice input
        setTimeout(() => {
          if (transcript.trim() && transcript.length >= 10) {
            console.log('Auto-submitting voice query...')
            // Call mutation directly
            mutation.mutate({
              query: transcript.trim(),
              sources: undefined,
              max_sources: 6,
              include_credibility: true,
              parent_research_id: currentResearchId || undefined,
            })
          } else {
            alert('Please speak at least 10 characters for a valid research query.')
          }
        }, 100)
      }

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please allow microphone access in your browser settings.')
        } else if (event.error === 'no-speech') {
          alert('No speech detected. Please try again.')
        } else {
          alert(`Speech recognition error: ${event.error}`)
        }
      }

      recognitionInstance.onend = () => {
        console.log('Speech recognition ended')
        setIsListening(false)
      }

      recognitionInstance.onstart = () => {
        console.log('Speech recognition started')
        setIsListening(true)
      }

      setRecognition(recognitionInstance)
      console.log('Web Speech API initialized successfully')
    } else {
      console.warn('Web Speech API not supported in this browser')
    }
  }, [mutation, currentResearchId])

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
            // Update the item in conversation history
            setConversationHistory(prev => 
              prev.map(item => item.id === data.id ? data : item)
            )
            console.log(`Updated research status to: ${data.status}`)
            
            // Close the connection on completion or failure
            if (data.status === 'completed' || data.status === 'failed') {
              console.log(`Research ${data.status}, closing SSE connection after ${messageCount} messages`)
              eventSource.close()
              setIsStreaming(false)
              setShowOrchestration(false)
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

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault()
    }
    
    console.log('Submit clicked, query length:', query.length)
    
    if (!query.trim() || query.length < 10) {
      console.log('Query too short, minimum 10 characters required')
      return
    }
    
    console.log('Submitting research query:', query)
    mutation.mutate({
      query: query.trim(),
      sources: undefined,
      max_sources: 6,
      include_credibility: true,
      parent_research_id: currentResearchId || undefined,  // Include parent ID for follow-ups
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

  const getStatusIconForResearch = (research: ResearchStatus) => {
    switch (research.status) {
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
          <CardTitle className="flex items-center gap-2">
            Research Query
            {isListening && (
              <span className="text-sm font-normal text-red-500 animate-pulse flex items-center gap-1">
                <Mic className="h-4 w-4" />
                Listening...
              </span>
            )}
          </CardTitle>
          <CardDescription>
            Enter your research question or click the 🎤 microphone to speak. We'll query web search, academic papers, GitHub, news, and more.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Textarea
                placeholder="Example: What are the latest breakthroughs in quantum computing?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="min-h-[120px] resize-none pr-14"
                disabled={isLoading}
              />
              {/* Voice Input Button */}
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={toggleVoiceInput}
                disabled={isLoading || !recognition}
                className={`absolute bottom-3 right-3 h-8 w-8 p-0 ${
                  isListening 
                    ? 'text-red-500 animate-pulse bg-red-50 dark:bg-red-950' 
                    : 'text-muted-foreground hover:text-primary hover:bg-accent'
                }`}
                title={isListening ? 'Listening... Click to stop' : 'Click to speak your research query'}
              >
                {isListening ? (
                  <MicOff className="h-4 w-4" />
                ) : (
                  <Mic className="h-4 w-4" />
                )}
              </Button>
            </div>
            
            {/* Sample Queries */}
            {!query && !researchStatus && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Sparkles className="h-4 w-4" />
                  <span>Try these sample queries:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {SAMPLE_QUERIES.map((sampleQuery, index) => (
                    <Button
                      key={index}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setQuery(sampleQuery)}
                      className="text-xs h-auto py-2 px-3 hover:bg-blue-50 dark:hover:bg-blue-950 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
                      disabled={isLoading}
                    >
                      {sampleQuery}
                    </Button>
                  ))}
                </div>
              </div>
            )}
            
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

      {/* Live Orchestration Status */}
      <OrchestrationStatus 
        isActive={showOrchestration && researchStatus?.status === 'processing'}
      />

      {/* Conversation History - Show all research items */}
      {conversationHistory.length > 0 && conversationHistory.map((research, index) => (
        <div key={research.id} className="space-y-6">
          {/* Query Header */}
          <Card className="bg-gradient-to-r from-slate-50 to-gray-50 dark:from-slate-900 dark:to-gray-900">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  {index === 0 ? (
                    <Search className="h-5 w-5 text-primary" />
                  ) : (
                    <MessageSquarePlus className="h-5 w-5 text-blue-500" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="text-xs text-muted-foreground mb-1">
                    {index === 0 ? 'Initial Query' : `Follow-up ${index}`}
                  </div>
                  <div className="font-medium text-lg">
                    {research.query}
                  </div>
                </div>
                {getStatusIconForResearch(research)}
              </div>
            </CardContent>
          </Card>

          {/* Status Card */}
          {research.status && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIconForResearch(research)}
                    <div>
                      <div className="font-medium">
                        Status: {research.status.charAt(0).toUpperCase() + research.status.slice(1)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {research.status === 'processing' && 'Querying sources and synthesizing results...'}
                        {research.status === 'completed' && 'Research completed successfully'}
                        {research.status === 'failed' && 'Research failed. Please try again.'}
                      </div>
                    </div>
                  </div>
                  
                  {research.credibility_score !== undefined && (
                    <Badge variant={research.credibility_score >= 0.7 ? 'default' : 'secondary'}>
                      Credibility: {(research.credibility_score * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Sources Panel */}
          {research.results && (
            <SourcesPanel results={research.results} />
          )}

          {/* Results Display */}
          {research.synthesis && (
            <ResultsDisplay
              synthesis={research.synthesis}
              credibilityScore={research.credibility_score}
            />
          )}

          {/* Error Display */}
          {research.error && (
            <Card className="border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                  <div>
                    <div className="font-medium text-red-900 dark:text-red-100">
                      Error
                    </div>
                    <div className="text-sm text-red-700 dark:text-red-300 mt-1">
                      {research.error}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      ))}

      {/* Follow-up Actions - Show only after latest completed research */}
      {researchStatus?.synthesis && researchStatus.status === 'completed' && (
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/50 dark:to-indigo-950/50 border-blue-200 dark:border-blue-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h3 className="font-semibold text-lg mb-1">Want to dive deeper?</h3>
                <p className="text-sm text-muted-foreground">
                  Ask a follow-up question or refine your research
                </p>
              </div>
              <Button
                onClick={() => {
                  setQuery('')
                  // Don't clear researchStatus or conversation - keep all for context
                  document.querySelector('textarea')?.focus()
                }}
                variant="default"
                className="gap-2"
              >
                <MessageSquarePlus className="h-4 w-4" />
                Ask Follow-up Question
              </Button>
            </div>
            
            {/* Suggested Follow-ups */}
            <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-800">
              <p className="text-sm font-medium mb-2">Suggested follow-ups:</p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setQuery(`What are the latest developments related to "${researchStatus.query?.substring(0, 50)}..."?`)}
                  className="text-xs"
                >
                  Latest developments
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setQuery(`Compare the pros and cons of "${researchStatus.query?.substring(0, 50)}..."`)}
                  className="text-xs"
                >
                  Pros vs Cons
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setQuery(`What are the alternatives to "${researchStatus.query?.substring(0, 50)}..."?`)}
                  className="text-xs"
                >
                  Show alternatives
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
