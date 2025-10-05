"""
Cerebras API Service
Handles ultra-fast inference using Llama 3.3 70B
Supports: Streaming, Structured Outputs, Tool Use, Reasoning
"""
import aiohttp
import asyncio
import json
from typing import AsyncIterator, Dict, List, Any, Optional
from loguru import logger

from app.core.config import settings
from app.core.monitoring import cerebras_api_calls_total
from app.schemas.synthesis import SYNTHESIS_JSON_SCHEMA, ResearchSynthesis


class CerebrasService:
    """Service for Cerebras API interactions with advanced capabilities"""
    
    def __init__(self):
        self.api_key = settings.CEREBRAS_API_KEY
        self.api_url = settings.CEREBRAS_API_URL
        self.model = settings.CEREBRAS_MODEL
        
    # Tool definitions for intelligent source selection
    MCP_TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "strict": True,
                "description": "Search the web for current information, news, and general knowledge. Best for recent events, current data, and broad topics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_arxiv",
                "strict": True,
                "description": "Search academic papers on ArXiv. Best for scientific research, academic papers, and peer-reviewed studies.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The academic search query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_github",
                "strict": True,
                "description": "Search GitHub repositories and code. Best for software development, open-source projects, and code examples.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The GitHub search query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_news",
                "strict": True,
                "description": "Search news articles from various sources. Best for current events, breaking news, and recent developments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The news search query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "strict": True,
                "description": "Query cached research results from previous queries. Best for retrieving past research and building on previous work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The database query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_documents",
                "strict": True,
                "description": "Search local documents and files. Best for accessing uploaded documents, PDFs, and local knowledge base.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The document search query"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        }
    ]
    
    async def synthesize(
        self,
        query: str,
        context: List[Dict[str, Any]],
        parent_context: Dict[str, Any] | None = None,
        stream: bool = True,
        use_structured_output: bool = True,
        use_reasoning: bool = True
    ) -> AsyncIterator[str] | str:
        """
        Synthesize research results using Cerebras Llama 3.3 70B
        Now with Structured Outputs and Reasoning support
        
        Args:
            query: Original research query
            context: List of results from various sources
            parent_context: Optional parent research context for follow-up queries
            stream: Whether to stream the response
            use_structured_output: Use JSON schema for structured responses
            use_reasoning: Enable reasoning capabilities
        
        Returns:
            Streaming or complete synthesis
        """
        try:
            # Build context summary
            context_text = self._build_context(context)
            
            # Build prompt (with parent context if available)
            prompt = self._build_synthesis_prompt(query, context_text, parent_context)
            
            # Determine reasoning effort based on query complexity
            reasoning_effort = self._determine_reasoning_effort(query) if use_reasoning else None
            
            logger.info(f"Synthesis: query_length={len(query)}, reasoning={reasoning_effort}, structured={use_structured_output}")
            
            # Make API call
            if stream:
                async for chunk in self._stream_completion(
                    prompt, 
                    reasoning_effort=reasoning_effort,
                    use_structured_output=use_structured_output
                ):
                    yield chunk
            else:
                result = await self._complete(
                    prompt,
                    reasoning_effort=reasoning_effort,
                    use_structured_output=use_structured_output
                )
                yield result
                return
                
        except Exception as e:
            logger.error(f"Cerebras synthesis error: {e}")
            cerebras_api_calls_total.labels(model=self.model, status="error").inc()
            raise
    
    def _determine_reasoning_effort(self, query: str) -> str:
        """
        Determine appropriate reasoning effort based on query complexity
        
        Returns:
            "low", "medium", or "high"
        """
        # Complexity indicators
        query_lower = query.lower()
        
        # High complexity indicators
        high_complexity_keywords = [
            'compare', 'analyze', 'evaluate', 'assess', 'contrast',
            'implications', 'impact', 'relationship', 'correlate',
            'explain why', 'explain how', 'reasoning', 'strategy'
        ]
        
        # Simple fact-finding indicators
        simple_keywords = [
            'what is', 'who is', 'when did', 'where is', 'define',
            'list', 'name', 'find', 'show me'
        ]
        
        # Check for high complexity
        if any(keyword in query_lower for keyword in high_complexity_keywords):
            return "high"
        
        # Check for simple queries
        if any(keyword in query_lower for keyword in simple_keywords):
            return "low"
        
        # Check query length (longer queries usually more complex)
        if len(query.split()) > 20:
            return "high"
        elif len(query.split()) < 8:
            return "low"
        
        # Default to medium
        return "medium"
    
    async def _stream_completion(
        self, 
        prompt: str,
        reasoning_effort: Optional[str] = None,
        use_structured_output: bool = False
    ) -> AsyncIterator[str]:
        """Stream completion from Cerebras API with optional structured output and reasoning"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI research assistant. Provide comprehensive, well-structured answers with clear citations. Focus on accuracy and relevance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 3000,
        }
        
        # Add reasoning effort if specified (for gpt-oss-120b model)
        if reasoning_effort and self.model == "gpt-oss-120b":
            payload["reasoning_effort"] = reasoning_effort
            logger.info(f"Using reasoning_effort: {reasoning_effort}")
        
        # Add structured output schema if requested
        # NOTE: Structured outputs with streaming requires collecting full response first
        if use_structured_output:
            payload["response_format"] = SYNTHESIS_JSON_SCHEMA
            logger.info("Using structured JSON output schema")
        
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
                                        chunk = json.loads(data)
                                        if 'choices' in chunk and len(chunk['choices']) > 0:
                                            delta = chunk['choices'][0].get('delta', {})
                                            
                                            # Handle reasoning content if present
                                            if 'reasoning' in delta:
                                                # Log reasoning tokens but don't stream them
                                                logger.debug(f"Reasoning: {delta['reasoning'][:100]}")
                                            
                                            # Stream main content
                                            content = delta.get('content', '')
                                            if content:
                                                yield content
                                    except json.JSONDecodeError:
                                        continue
                                        
        except asyncio.TimeoutError:
            logger.error("Cerebras API timeout")
            cerebras_api_calls_total.labels(model=self.model, status="timeout").inc()
            raise Exception("Cerebras API timeout")
    
    async def _complete(
        self, 
        prompt: str,
        reasoning_effort: Optional[str] = None,
        use_structured_output: bool = False
    ) -> str:
        """Get complete response from Cerebras API with optional structured output and reasoning"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI research assistant. Provide comprehensive, well-structured answers with clear citations. Focus on accuracy and relevance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 3000,
        }
        
        # Add reasoning effort if specified
        if reasoning_effort and self.model == "gpt-oss-120b":
            payload["reasoning_effort"] = reasoning_effort
        
        # Add structured output schema if requested
        if use_structured_output:
            payload["response_format"] = SYNTHESIS_JSON_SCHEMA
        
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
                    
                    # Handle structured response
                    content = result['choices'][0]['message']['content']
                    
                    # Log reasoning if present
                    if 'reasoning' in result['choices'][0]['message']:
                        reasoning = result['choices'][0]['message']['reasoning']
                        logger.info(f"Reasoning tokens: {len(reasoning)} chars")
                    
                    return content
                    
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
    
    def _build_synthesis_prompt(self, query: str, context: str, parent_context: Dict[str, Any] | None = None) -> str:
        """Build synthesis prompt with optional conversation history"""
        
        # If this is a follow-up, include parent context
        if parent_context and parent_context.get('synthesis'):
            return f"""This is a FOLLOW-UP question in an ongoing research conversation.

PREVIOUS RESEARCH CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Previous Question: {parent_context.get('query', 'Unknown')}

Previous Answer (Summary):
{parent_context.get('synthesis', 'No previous context')[:1000]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT FOLLOW-UP QUESTION: {query}

NEW Information from multiple sources:

{context}

Instructions:
1. This is a FOLLOW-UP question - use the PREVIOUS RESEARCH CONTEXT above to understand what we're building on
2. Answer the follow-up question DIRECTLY, referencing the previous context when relevant
3. If the user asks "compare", "what about", "how do they differ" etc., they're asking about things mentioned in the previous answer
4. Use a conversational, easy-to-read style like Perplexity or ChatGPT
5. Format with clear sections using markdown:
   - Use ## for main sections
   - Use numbered lists (1., 2., 3.) or bullet points as appropriate
   - Use **bold** for important terms
   - Use code blocks for technical details if relevant

6. Structure should be natural and flow based on the question:
   - For "compare": Show side-by-side comparison with the previous answer
   - For "latest developments": Focus on what's new since the previous research
   - For "pros and cons": Compare benefits and drawbacks
   - For "alternatives": Show other options than what was previously discussed

7. Keep it comprehensive but scannable - use short paragraphs
8. End with a brief "Sources" section listing what each source contributed
9. Be specific with names, numbers, and facts - avoid vague generalizations

Remember: You have the context of the previous conversation. Use it to give a coherent, connected answer!"""
        
        # Otherwise, this is an initial query
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
    
    async def complete_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Complete a chat request with tool calling support.
        Returns the model's response including any tool calls.
        """
        if tools is None:
            tools = self.MCP_TOOLS
        
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "max_tokens": max_tokens,
            "temperature": 0.3,  # Lower temperature for more deterministic tool selection
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Cerebras tool calling request: {len(messages)} messages, {len(tools)} tools available")
                
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Cerebras API error: {response.status} - {error_text}")
                        raise Exception(f"Cerebras API error: {response.status}")
                    
                    data = await response.json()
                    cerebras_api_calls_total.inc()
                    
                    # Extract response
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        message = choice.get("message", {})
                        
                        result = {
                            "content": message.get("content", ""),
                            "tool_calls": message.get("tool_calls", []),
                            "finish_reason": choice.get("finish_reason", "stop")
                        }
                        
                        logger.info(f"Cerebras response: finish_reason={result['finish_reason']}, tool_calls={len(result['tool_calls'])}")
                        return result
                    else:
                        logger.error(f"Unexpected Cerebras response format: {data}")
                        raise Exception("Unexpected response format from Cerebras API")
                        
        except asyncio.TimeoutError:
            logger.error("Cerebras API request timed out")
            raise Exception("Cerebras API request timed out")
        except Exception as e:
            logger.error(f"Error in Cerebras tool calling: {e}")
            raise

