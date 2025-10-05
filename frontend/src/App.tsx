import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { ResearchInterface } from './components/ResearchInterface'
import { ResearchHistory } from './components/ResearchHistory'
import { Header } from './components/Header'
import { Footer } from './components/Footer'

const queryClient = new QueryClient()

function App() {
  const [selectedQuery, setSelectedQuery] = useState<{ query: string; id: string } | null>(null)

  const handleSelectQuery = (query: string, id: string) => {
    setSelectedQuery({ query, id })
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Research Interface */}
            <div className="lg:col-span-3">
              <ResearchInterface 
                initialQuery={selectedQuery?.query}
                initialResearchId={selectedQuery?.id}
              />
            </div>
            
            {/* Research History Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-4">
                <ResearchHistory onSelectQuery={handleSelectQuery} />
              </div>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </QueryClientProvider>
  )
}

export default App

