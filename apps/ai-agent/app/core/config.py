"""
NOVYRA AI Engine — Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent
APP_DIR = CONFIG_DIR.parent
AI_AGENT_DIR = APP_DIR.parent
ENV_FILE_PATH = AI_AGENT_DIR / ".env"


class Settings(BaseSettings):
    """NOVYRA application settings"""

    # Google Gemini (primary LLM)
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.3

    # Neo4j Knowledge Graph
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "novyra_neo4j"

    # PostgreSQL
    DATABASE_URL: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Auth
    AI_BACKEND_TOKEN: str = ""
    SECRET_KEY: str = "novyra-secret-change-in-prod"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5000"

    # Upload storage
    UPLOAD_DIR: str = "/app/data/uploads"

    # Debug
    DEBUG: bool = False

    def get_allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = str(ENV_FILE_PATH)
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
logger.info("NOVYRA config loaded | LLM: %s | Neo4j: %s", settings.LLM_MODEL, settings.NEO4J_URI)


def validate_settings():
    issues = []
    if not settings.GOOGLE_API_KEY:
        issues.append("GOOGLE_API_KEY not set — LLM calls will fail")
    if not settings.DATABASE_URL:
        issues.append("DATABASE_URL not set — DB features disabled")
    for issue in issues:
        logger.warning("⚠️  %s", issue)
    return True



class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"  # Updated default model
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str = ""
    
    # LangChain Configuration
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "entropy-ai-agent"
    
    # Vector Store Configuration
    vector_store_path: str = "./data/vector_store"
    embeddings_model: str = "ggml-all-MiniLM-L6-v2-f16.gguf"  # GPT4All model
    embeddings_device: str = "cpu"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse allowed_origins from comma-separated string"""
        if isinstance(v, str):
            return v
        return v
    
    def get_allowed_origins_list(self):
        """Get allowed origins as a list"""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
        return self.allowed_origins
    
    class Config:
        env_file = str(ENV_FILE_PATH)
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Create settings instance
print(f"📦 Loading environment variables from: {ENV_FILE_PATH}")
settings = Settings()

# Print loaded configuration (without sensitive data)
print(f"⚙️  Loaded Configuration:")
print(f"   - GROQ_API_KEY: {'✅ Set' if settings.groq_api_key and settings.groq_api_key != 'your_groq_api_key_here' else '❌ Not set'}")
print(f"   - GROQ_MODEL: {settings.groq_model}")
print(f"   - HOST: {settings.host}")
print(f"   - PORT: {settings.port}")
print(f"   - DATABASE_URL: {'✅ Set' if settings.database_url else '❌ Not set'}")
if settings.database_url:
    # Show database info without password
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    db_info = f"{parsed.scheme}://{parsed.username}@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"   - Database: {db_info}")
print(f"   - ALLOWED_ORIGINS: {settings.get_allowed_origins_list()}")
print(f"   - LOG_LEVEL: {settings.log_level}")


def validate_settings():
    """Validate critical settings"""
    issues = []
    
    if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
        issues.append("⚠️  GROQ_API_KEY not set - LLM features will fail")
    
    if not settings.database_url:
        issues.append("⚠️  DATABASE_URL is not set. Chat history will not be persisted.")
    elif 'pgbouncer' in settings.database_url.lower():
        issues.append("⚠️  DATABASE_URL contains 'pgbouncer' parameter which will be removed for compatibility")
    
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   {issue}")
    
    print("✅ Configuration settings validation complete")
    return True
