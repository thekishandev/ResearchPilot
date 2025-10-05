import axios from 'axios'
import { ResearchQuery, ResearchResponse, ResearchStatus } from '@/types/research'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function submitResearch(data: ResearchQuery): Promise<ResearchResponse> {
  const response = await api.post('/research/query', data)
  return response.data
}

export async function getResearchStatus(researchId: string): Promise<ResearchStatus> {
  const response = await api.get(`/research/${researchId}`)
  return response.data
}

export async function getSourcesStatus() {
  const response = await api.get('/sources/status')
  return response.data
}

export async function getHealth() {
  const response = await api.get('/health')
  return response.data
}
