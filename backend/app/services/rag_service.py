"""RAG service for storing and retrieving classification examples."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.config import settings
from app.models.rag import RAGExample
from app.services.embedding import embedding_service


class RAGService:
    """Service for RAG operations with ChromaDB."""
    
    def __init__(self):
        """Initialize RAG service with ChromaDB."""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = "waste_classification_examples"
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get or create the ChromaDB collection."""
        try:
            return self.client.get_collection(name=self.collection_name)
        except Exception:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Waste classification examples for RAG"}
            )
    
    def add_example(self, example: RAGExample) -> str:
        """
        Add a classification example to the RAG database.
        
        Args:
            example: RAGExample object to add
            
        Returns:
            ID of the added example
        """
        import uuid
        example_id = str(uuid.uuid4())
        
        # Store in ChromaDB
        self.collection.add(
            ids=[example_id],
            embeddings=[example.text_embedding],
            documents=[example.text_description],
            metadatas=[{
                "item_name": example.item_name,
                "category": example.category,
                "bin_color": example.bin_color,
                "bin_type": example.bin_type,
                "rules": example.rules or "",
            }]
        )
        
        return example_id
    
    def add_examples_batch(self, examples: List[RAGExample]) -> List[str]:
        """
        Add multiple examples to the RAG database.
        
        Args:
            examples: List of RAGExample objects
            
        Returns:
            List of IDs of added examples
        """
        import uuid
        ids = [str(uuid.uuid4()) for _ in examples]
        
        self.collection.add(
            ids=ids,
            embeddings=[ex.text_embedding for ex in examples],
            documents=[ex.text_description for ex in examples],
            metadatas=[{
                "item_name": ex.item_name,
                "category": ex.category,
                "bin_color": ex.bin_color,
                "bin_type": ex.bin_type,
                "rules": ex.rules or "",
            } for ex in examples]
        )
        
        return ids
    
    def retrieve_similar(
        self,
        text: Optional[str] = None,
        text_embedding: Optional[List[float]] = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar examples from RAG database.
        
        Args:
            text: Text query (will be embedded if provided)
            text_embedding: Pre-computed text embedding
            top_k: Number of results to return
            
        Returns:
            List of similar examples with metadata
        """
        if top_k is None:
            top_k = settings.RAG_TOP_K
        
        # Get embedding
        if text_embedding is None:
            if not text:
                return []
            text_embedding = embedding_service.generate_text_embedding(text)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[text_embedding],
            n_results=top_k
        )
        
        # Format results
        similar_examples = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                similar_examples.append({
                    "item_name": results['metadatas'][0][i].get("item_name", "Unknown"),
                    "text_description": results['documents'][0][i],
                    "category": results['metadatas'][0][i].get("category", "general"),
                    "bin_color": results['metadatas'][0][i].get("bin_color", "other"),
                    "bin_type": results['metadatas'][0][i].get("bin_type", "General waste"),
                    "rules": results['metadatas'][0][i].get("rules", ""),
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return similar_examples
    
    def check_duplicate(
        self,
        text_description: str,
        similarity_threshold: float = 0.95
    ) -> bool:
        """
        Check if a similar example already exists in the database.
        
        Args:
            text_description: Text description to check
            similarity_threshold: Minimum similarity to consider a duplicate (0.0-1.0)
                                Lower values = more strict (0.95 means 95% similar)
        
        Returns:
            True if a duplicate exists, False otherwise
        """
        try:
            # Generate embedding for the description
            text_embedding = embedding_service.generate_text_embedding(text_description)
            
            # Query for similar items (check top 5)
            results = self.collection.query(
                query_embeddings=[text_embedding],
                n_results=5
            )
            
            # Check if any result is very similar (distance < threshold)
            # ChromaDB uses cosine distance: 0 = identical, 1 = completely different
            # We convert similarity threshold to distance: distance = 1 - similarity
            distance_threshold = 1.0 - similarity_threshold
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i] if 'distances' in results else 1.0
                    if distance <= distance_threshold:
                        # Found a very similar example
                        return True
            
            return False
        except Exception as e:
            print(f"Error checking for duplicate: {e}")
            # On error, assume no duplicate (safer to add than skip)
            return False
    
    def get_all_examples(self) -> List[Dict[str, Any]]:
        """Get all examples from the database (for admin purposes)."""
        results = self.collection.get()
        
        examples = []
        if results['ids']:
            for i in range(len(results['ids'])):
                examples.append({
                    "id": results['ids'][i],
                    "item_name": results['metadatas'][i].get("item_name", "Unknown"),
                    "text_description": results['documents'][i],
                    "category": results['metadatas'][i].get("category", "general"),
                    "bin_color": results['metadatas'][i].get("bin_color", "other"),
                    "bin_type": results['metadatas'][i].get("bin_type", "General waste"),
                    "rules": results['metadatas'][i].get("rules", ""),
                })
        
        return examples
    
    def clear_collection(self):
        """Clear all examples from the collection (use with caution)."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()


# Global instance
rag_service = RAGService()
