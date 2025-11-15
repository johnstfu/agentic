"""
Configuration centrale pour l'application
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration centralisée"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    # OpenAI Settings
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_TEMPERATURE = 0.1

    # Tavily Settings
    TAVILY_MAX_RESULTS = 8
    TAVILY_SEARCH_DEPTH = "advanced"

    # Cache Settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 heure en secondes

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 10

    # App Settings
    APP_NAME = "VérificateurIA"
    APP_VERSION = "3.0.0"
    MAX_SOURCES_DISPLAY = 10
    
    # Version Settings (v3.0)
    DEFAULT_VERSION = "v3.0"  # "v2.0" or "v3.0"
    ENABLE_VERSION_SELECTOR = True
    
    # v3.0 Settings
    ENABLE_HITL_BY_DEFAULT = True
    ENABLE_PERSISTENCE = True
    ENABLE_MULTI_STEP_REASONING = True
    ENABLE_FEEDBACK = True
    BATCH_MAX_CLAIMS = 10
    
    # Database paths
    PERSISTENCE_DB = "fact_checks.db"
    FEEDBACK_DB = "feedback.db"

    @classmethod
    def validate(cls):
        """Valide que les clés API sont présentes"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY manquante dans .env")
        if not cls.TAVILY_API_KEY:
            raise ValueError("❌ TAVILY_API_KEY manquante dans .env")
        return True
