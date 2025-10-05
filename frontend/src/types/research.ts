export interface ResearchQuery {
  query: string
  sources?: string[]
  max_sources?: number
  include_credibility?: boolean
  parent_research_id?: string
}

export interface ResearchResponse {
  id: string
  status: string
  message: string
}

export interface SourceResult {
  source: string
  status: string
  data?: any
  error?: string
  response_time?: number
}

export interface ResearchStatus {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  query: string
  sources: string[]
  results?: SourceResult[]
  synthesis?: string
  credibility_score?: number
  created_at: string
  completed_at?: string
  error?: string
}

export interface SourceHealth {
  name: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  response_time?: number
  last_check?: string
  error?: string
}
