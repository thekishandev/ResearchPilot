"""
Application Configuration
Loads settings from environment variables
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SECRET_KEY: str = Field(default="change-this-in-production", env="SECRET_KEY")
    
    # Cerebras API
    CEREBRAS_API_KEY: str = Field(..., env="CEREBRAS_API_KEY")
    CEREBRAS_API_URL: str = Field(
        default="https://api.cerebras.ai/v1/chat/completions",
        env="CEREBRAS_API_URL"
    )
    CEREBRAS_MODEL: str = Field(default="llama-3.3-70b", env="CEREBRAS_MODEL")
    
    # Ollama (Local Llama)
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    OLLAMA_MODEL: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://researchpilot:researchpilot@localhost:5432/researchpilot",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    
    # MCP Gateway
    MCP_GATEWAY_URL: str = Field(default="http://localhost:8080", env="MCP_GATEWAY_URL")
    MCP_GATEWAY_TIMEOUT: int = Field(default=30, env="MCP_GATEWAY_TIMEOUT")
    
    # External APIs
    NEWS_API_KEY: str = Field(default="", env="NEWS_API_KEY")
    GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Performance
    MAX_CONCURRENT_SOURCES: int = Field(default=6, env="MAX_CONCURRENT_SOURCES")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    STREAM_CHUNK_SIZE: int = Field(default=1024, env="STREAM_CHUNK_SIZE")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
