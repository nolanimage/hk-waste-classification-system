"""Embedding generation service using sentence-transformers."""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        # Use a lightweight, multilingual model that works well for similarity search
        # all-MiniLM-L6-v2 is fast and works well for English text
        model_name = getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        try:
            self.model = SentenceTransformer(model_name)
            print(f"Loaded embedding model: {model_name}")
        except Exception as e:
            print(f"Warning: Could not load sentence-transformers model: {e}")
            print("Falling back to simple hash-based embeddings")
            self.model = None
    
    def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence-transformers.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            if self.model is not None:
                # Use sentence-transformers model
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # Fallback: simple hash-based embedding
                # This is a basic fallback if sentence-transformers fails to load
                import hashlib
                hash_obj = hashlib.sha256(text.encode())
                hash_hex = hash_obj.hexdigest()
                # Convert to float vector (simple approach)
                embedding = [float(int(hash_hex[i:i+2], 16)) / 255.0 for i in range(0, min(64, len(hash_hex)), 2)]
                # Pad or truncate to 384 dimensions (matching all-MiniLM-L6-v2)
                while len(embedding) < 384:
                    embedding.append(0.0)
                return embedding[:384]
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.generate_text_embedding(text) for text in texts]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        dot_product = np.dot(vec1_array, vec2_array)
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global instance
embedding_service = EmbeddingService()
