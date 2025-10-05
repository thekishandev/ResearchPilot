import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ResearchInterface } from './components/ResearchInterface'
import { Header } from './components/Header'
import { Footer } from './components/Footer'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <ResearchInterface />
        </main>
        <Footer />
      </div>
    </QueryClientProvider>
  )
}

export default App
