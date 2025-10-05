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
                    "content": "You are an expert research analyst. Synthesize information from multiple sources into a comprehensive, well-structured report."
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
                    "content": "You are an expert research analyst. Synthesize information from multiple sources into a comprehensive, well-structured report."
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
                context_parts.append(f"\n## Source {idx}: {source_name}\n")
                
                # Format data based on source type
                if isinstance(data, dict):
                    for key, value in data.items():
                        context_parts.append(f"**{key}**: {value}\n")
                elif isinstance(data, list):
                    for item in data[:5]:  # Limit to top 5 items
                        context_parts.append(f"- {item}\n")
                else:
                    context_parts.append(str(data))
        
        return ''.join(context_parts) if context_parts else "No data available from sources."
    
    def _build_synthesis_prompt(self, query: str, context: str) -> str:
        """Build synthesis prompt"""
        return f"""Research Query: {query}

Based on the following information from multiple sources, provide a comprehensive research synthesis.

{context}

Structure your response as follows:

# Executive Summary
Provide a concise 2-3 sentence overview of the key findings and their significance.

# Key Findings
Present 3-5 major discoveries or insights as bullet points:
- Each finding should be clear and actionable
- Include specific data points or metrics where available
- Highlight trends and patterns

# Detailed Analysis
Break down the research into logical subsections:
- Use ### subheadings for different aspects
- Include supporting evidence and examples
- Connect findings to the original query
- Explain implications and context

# Conclusions & Recommendations
- Summarize the most important takeaways
- Provide actionable recommendations
- Identify areas for further research
- Note any limitations or caveats

# Sources
List the sources consulted with brief descriptions of what each contributed.

Use clear markdown formatting with headers, bullet points, and **bold** for emphasis. Be concise yet comprehensive."""
