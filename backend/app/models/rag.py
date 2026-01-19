"""RAG data models for storing classification examples."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class RAGExample(BaseModel):
    """A single classification example for RAG."""
    text_description: str
    image_embedding: Optional[List[float]] = None
    text_embedding: List[float]
    category: str
    bin_color: str
    bin_type: str
    rules: Optional[str] = None
    item_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "text_description": self.text_description,
            "image_embedding": self.image_embedding,
            "text_embedding": self.text_embedding,
            "category": self.category,
            "bin_color": self.bin_color,
            "bin_type": self.bin_type,
            "rules": self.rules,
            "item_name": self.item_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RAGExample":
        """Create from dictionary."""
        return cls(**data)


class SeedExample(BaseModel):
    """Seed example format from JSON."""
    item_name: str
    text_description: str
    category: str
    bin_color: str
    bin_type: str
    rules: Optional[str] = None
    image_path: Optional[str] = None
