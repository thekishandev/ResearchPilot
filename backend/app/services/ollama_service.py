"""
Ollama Service
Handles local Llama 3.1 8B inference for credibility scoring
"""
import aiohttp
import asyncio
from typing import Dict, Any
from loguru import logger

from app.core.config import settings
from app.core.monitoring import ollama_api_calls_total


class OllamaService:
    """Service for Ollama local inference"""
    
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
    
    async def score_credibility(
        self,
        query: str,
        synthesis: str,
        sources: list
    ) -> Dict[str, Any]:
        """
        Score the credibility of research synthesis using local Llama
        
        Args:
            query: Original query
            synthesis: Generated synthesis
            sources: List of sources used
        
        Returns:
            Credibility score and reasoning
        """
        try:
            prompt = self._build_credibility_prompt(query, synthesis, sources)
            
            response = await self._generate(prompt)
            
            # Parse response to extract score
            score = self._parse_credibility_score(response)
            
            ollama_api_calls_total.labels(model=self.model, status="success").inc()
            
            return {
                "score": score,
                "reasoning": response,
                "model": self.model,
            }
            
        except Exception as e:
            logger.error(f"Ollama credibility scoring error: {e}")
            ollama_api_calls_total.labels(model=self.model, status="error").inc()
            return {
                "score": 0.5,
                "reasoning": "Unable to compute credibility score",
                "error": str(e),
            }
    
    async def _generate(self, prompt: str) -> str:
        """Generate response using Ollama"""
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more factual scoring
                "num_predict": 500,
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)  # Reduced to 10 seconds
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.warning(f"Ollama API error: {response.status} - {error_text}")
                        raise Exception(f"Ollama API error: {response.status}")
                    
                    result = await response.json()
                    return result.get('response', '')
                    
        except asyncio.TimeoutError:
            logger.warning("Ollama API timeout (10s) - model may be unavailable")
            raise Exception("Ollama API timeout")
        except Exception as e:
            logger.warning(f"Ollama generate error: {e}")
            raise
    
    async def check_health(self) -> bool:
        """Check if Ollama is healthy and model is available"""
        try:
            url = f"{self.host}/api/tags"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [m['name'] for m in data.get('models', [])]
                        return self.model in models
                    return False
                    
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def _build_credibility_prompt(
        self,
        query: str,
        synthesis: str,
        sources: list
    ) -> str:
        """Build prompt for credibility scoring"""
        sources_text = ', '.join(sources) if sources else 'multiple sources'
        
        return f"""You are a research credibility analyst. Evaluate the credibility of this research synthesis.

Query: {query}

Synthesis:
{synthesis}

Sources Used: {sources_text}

Analyze and provide a credibility score from 0.0 to 1.0 based on:
1. Source diversity and reliability
2. Factual accuracy indicators
3. Internal consistency
4. Citation quality
5. Balanced perspective

Respond with:
Score: [0.0-1.0]
Reasoning: [Your analysis]
"""
    
    def _parse_credibility_score(self, response: str) -> float:
        """Parse credibility score from response"""
        try:
            # Look for "Score: X.X" pattern
            import re
            score_match = re.search(r'Score:\s*(0?\.\d+|1\.0)', response, re.IGNORECASE)
            
            if score_match:
                score = float(score_match.group(1))
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
            # Fallback: look for any number between 0 and 1
            number_match = re.search(r'\b(0?\.\d+|1\.0)\b', response)
            if number_match:
                score = float(number_match.group(1))
                return max(0.0, min(1.0, score))
            
            # Default to 0.5 if no score found
            return 0.5
            
        except Exception as e:
            logger.error(f"Error parsing credibility score: {e}")
            return 0.5
