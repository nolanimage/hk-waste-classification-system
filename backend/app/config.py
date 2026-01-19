"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings."""
    
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "qwen/qwen3-vl-32b-instruct")
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", "qwen/qwen-2.5-7b-instruct")  # For text-only inputs
    ITEM_DETECTION_MODEL: str = os.getenv("ITEM_DETECTION_MODEL", "qwen/qwen-2.5-72b-instruct")  # For item detection/splitting
    
    # Embeddings (using sentence-transformers, no API key needed)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # ChromaDB
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Server
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # RAG Settings
    RAG_TOP_K: int = 5  # Number of similar examples to retrieve
    
    @property
    def openrouter_base_url(self) -> str:
        """OpenRouter API base URL."""
        return "https://openrouter.ai/api/v1"
    
    @property
    def openrouter_headers(self) -> dict:
        """OpenRouter API headers."""
        return {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/your-repo",
            "X-Title": "Waste Classification System",
        }

settings = Settings()
