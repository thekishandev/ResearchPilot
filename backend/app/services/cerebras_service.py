"""
Cerebras API Service
Handles ultra-fast inference using Llama 3.3 70B
"""
import aiohttp
import asyncio
from typing import AsyncIterator, Dict, List, Any
from loguru import logger

from app.core.config import settings
from app.core.monitoring import cerebras_api_calls_total


class CerebrasService:
    """Service for Cerebras API interactions"""
    
    def __init__(self):
        self.api_key = settings.CEREBRAS_API_KEY
        self.api_url = settings.CEREBRAS_API_URL
        self.model = settings.CEREBRAS_MODEL
    
    async def synthesize(
        self,
        query: str,
        context: List[Dict[str, Any]],
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        """
        Synthesize research results using Cerebras Llama 3.3 70B
        
        Args:
            query: Original research query
            context: List of results from various sources
            stream: Whether to stream the response
        
        Returns:
            Streaming or complete synthesis
        """
        try:
            # Build context summary
            context_text = self._build_context(context)
            
            # Build prompt
            prompt = self._build_synthesis_prompt(query, context_text)
            
            # Make API call
            if stream:
                async for chunk in self._stream_completion(prompt):
                    yield chunk
            else:
                result = await self._complete(prompt)
                yield result
                return
                
        except Exception as e:
            logger.error(f"Cerebras synthesis error: {e}")
            cerebras_api_calls_total.labels(model=self.model, status="error").inc()
            raise
    
    async def _stream_completion(self, prompt: str) -> AsyncIterator[str]:
        """Stream completion from Cerebras API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant like Perplexity. Answer questions directly and conversationally. Focus on what the user asked for. Use clear formatting with headers, bullet points, and numbered lists. Be comprehensive but concise. Always cite sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Cerebras API error: {response.status} - {error_text}")
                        cerebras_api_calls_total.labels(model=self.model, status="error").inc()
                        raise Exception(f"Cerebras API error: {response.status}")
                    
                    cerebras_api_calls_total.labels(model=self.model, status="success").inc()
                    
                    # Stream response chunks
                    async for line in response.content:
                        if line:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data: '):
                                data = line_text[6:]
                                if data != '[DONE]':
                                    try:
                                        import json
                                        chunk = json.loads(data)
                                        if 'choices' in chunk and len(chunk['choices']) > 0:
                                            delta = chunk['choices'][0].get('delta', {})
                                            content = delta.get('content', '')
                                            if content:
                                                yield content
                                    except json.JSONDecodeError:
                                        continue
                                        
        except asyncio.TimeoutError:
            logger.error("Cerebras API timeout")
            cerebras_api_calls_total.labels(model=self.model, status="timeout").inc()
            raise Exception("Cerebras API timeout")
    
    async def _complete(self, prompt: str) -> str:
        """Get complete response from Cerebras API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant like Perplexity. Answer questions directly and conversationally. Focus on what the user asked for. Use clear formatting with headers, bullet points, and numbered lists. Be comprehensive but concise. Always cite sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Cerebras API error: {response.status} - {error_text}")
                        cerebras_api_calls_total.labels(model=self.model, status="error").inc()
                        raise Exception(f"Cerebras API error: {response.status}")
                    
                    result = await response.json()
                    cerebras_api_calls_total.labels(model=self.model, status="success").inc()
                    
                    return result['choices'][0]['message']['content']
                    
        except asyncio.TimeoutError:
            logger.error("Cerebras API timeout")
            cerebras_api_calls_total.labels(model=self.model, status="timeout").inc()
            raise Exception("Cerebras API timeout")
    
    def _build_context(self, context: List[Dict[str, Any]]) -> str:
        """Build context summary from multiple sources"""
        context_parts = []
        
        for idx, source_result in enumerate(context, 1):
            source_name = source_result.get('source', 'Unknown')
            status = source_result.get('status', 'unknown')
            
            if status == 'success' and source_result.get('data'):
                data = source_result['data']
                context_parts.append(f"\n## {source_name.replace('-', ' ').title()}\n")
                
                # Format data based on source type
                if isinstance(data, dict):
                    # Handle structured data (like search results)
                    if 'results' in data:
                        results = data['results']
                        if isinstance(results, list):
                            for i, item in enumerate(results[:10], 1):  # Top 10 results
                                if isinstance(item, dict):
                                    title = item.get('title', item.get('name', f'Result {i}'))
                                    snippet = item.get('snippet', item.get('description', item.get('body', '')))
                                    url = item.get('url', item.get('link', ''))
                                    
                                    context_parts.append(f"\n**{i}. {title}**\n")
                                    if snippet:
                                        context_parts.append(f"{snippet[:200]}...\n")
                                    if url:
                                        context_parts.append(f"Source: {url}\n")
                                else:
                                    context_parts.append(f"{i}. {str(item)[:200]}\n")
                    else:
                        # Generic dict formatting
                        for key, value in data.items():
                            if key not in ['count', 'source']:  # Skip metadata
                                context_parts.append(f"**{key.replace('_', ' ').title()}**: {str(value)[:300]}\n")
                
                elif isinstance(data, list):
                    for i, item in enumerate(data[:10], 1):
                        if isinstance(item, dict):
                            # Format dict items nicely
                            title = item.get('title', item.get('name', f'Item {i}'))
                            context_parts.append(f"\n{i}. **{title}**\n")
                            for k, v in item.items():
                                if k not in ['title', 'name'] and v:
                                    context_parts.append(f"   - {k.replace('_', ' ').title()}: {str(v)[:150]}\n")
                        else:
                            context_parts.append(f"{i}. {str(item)[:200]}\n")
                else:
                    context_parts.append(f"{str(data)[:500]}\n")
                
                context_parts.append("\n")
        
        return ''.join(context_parts) if context_parts else "No data available from sources."
    
    def _build_synthesis_prompt(self, query: str, context: str) -> str:
        """Build synthesis prompt"""
        return f"""User Question: {query}

Information from multiple sources:

{context}

Instructions:
1. Answer the user's question DIRECTLY - if they ask for "Top 10", list 10 items with clear rankings
2. Use a conversational, easy-to-read style like Perplexity or ChatGPT
3. Format with clear sections using markdown:
   - Use ## for main sections
   - Use numbered lists (1., 2., 3.) or bullet points as appropriate
   - Use **bold** for important terms and model names
   - Use code blocks for technical details if relevant

4. Structure should be natural and flow based on the question:
   - For "Top 10" or rankings: Start with a brief intro, then numbered list with details
   - For "What is" questions: Define clearly, then explain with examples
   - For "How to" questions: Step-by-step guide
   - For comparisons: Side-by-side analysis with pros/cons

5. Keep it comprehensive but scannable - use short paragraphs
6. End with a brief "Sources" section listing what each source contributed
7. Be specific with names, numbers, and facts - avoid vague generalizations

Remember: Answer exactly what the user asked for in a direct, helpful way."""
