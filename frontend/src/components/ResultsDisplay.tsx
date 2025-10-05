import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Award, Download, FileText } from 'lucide-react'
import { Button } from './ui/button'

interface ResultsDisplayProps {
  synthesis: string
  credibilityScore?: number
}

export function ResultsDisplay({ synthesis, credibilityScore }: ResultsDisplayProps) {
  const handleDownload = () => {
    const timestamp = new Date().toISOString().split('T')[0]
    const blob = new Blob([synthesis], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-synthesis-${timestamp}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getCredibilityColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    if (score >= 0.6) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  }

  return (
    <Card className="border-2 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 border-b">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            <CardTitle className="text-2xl font-bold">Research Synthesis</CardTitle>
            {credibilityScore !== undefined && (
              <Badge
                className={`flex items-center gap-1.5 px-3 py-1 ${getCredibilityColor(credibilityScore)}`}
              >
                <Award className="h-4 w-4" />
                {(credibilityScore * 100).toFixed(0)}% Credibility
              </Badge>
            )}
          </div>
          <Button onClick={handleDownload} variant="outline" size="sm" className="gap-2">
            <Download className="h-4 w-4" />
            Download Report
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="prose prose-slate dark:prose-invert max-w-none 
                      prose-headings:font-bold prose-headings:tracking-tight
                      prose-h1:text-3xl prose-h1:mb-6 prose-h1:mt-8 prose-h1:pb-3 prose-h1:border-b-2 prose-h1:border-blue-200 dark:prose-h1:border-blue-800
                      prose-h2:text-2xl prose-h2:mb-4 prose-h2:mt-6 prose-h2:text-blue-700 dark:prose-h2:text-blue-300
                      prose-h3:text-xl prose-h3:mb-3 prose-h3:mt-4 prose-h3:text-gray-800 dark:prose-h3:text-gray-200
                      prose-p:text-base prose-p:leading-relaxed prose-p:mb-4
                      prose-ul:my-4 prose-ul:space-y-2
                      prose-li:text-base prose-li:leading-relaxed
                      prose-strong:text-blue-600 dark:prose-strong:text-blue-400 prose-strong:font-semibold
                      prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:pl-4 prose-blockquote:italic
                      prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
                      prose-pre:bg-gray-900 prose-pre:text-gray-100">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({node, ...props}) => (
                <h1 className="flex items-center gap-2" {...props}>
                  <span className="inline-block w-1.5 h-8 bg-blue-600 rounded"></span>
                  {props.children}
                </h1>
              ),
              ul: ({node, ...props}) => (
                <ul className="list-disc pl-6 space-y-2" {...props} />
              ),
              ol: ({node, ...props}) => (
                <ol className="list-decimal pl-6 space-y-2" {...props} />
              ),
            }}
          >
            {synthesis}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  )
}

