"""Script to seed the RAG database with initial examples."""
import json
import os
from pathlib import Path
from app.services.rag_service import rag_service
from app.services.embedding import embedding_service
from app.models.rag import RAGExample, SeedExample


def load_seed_data() -> list[SeedExample]:
    """Load seed examples from JSON file."""
    data_path = Path(__file__).parent.parent.parent / "data" / "seed_examples.json"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {data_path}")
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [SeedExample(**item) for item in data]


def seed_rag_database():
    """Seed the RAG database with initial examples."""
    print("Loading seed data...")
    seed_examples = load_seed_data()
    
    print(f"Found {len(seed_examples)} examples to add.")
    print("Generating embeddings and adding to database...")
    
    rag_examples = []
    for seed in seed_examples:
        # Generate text embedding
        text_embedding = embedding_service.generate_text_embedding(
            seed.text_description
        )
        
        # Create RAG example
        rag_example = RAGExample(
            text_description=seed.text_description,
            text_embedding=text_embedding,
            category=seed.category,
            bin_color=seed.bin_color,
            bin_type=seed.bin_type,
            rules=seed.rules,
            item_name=seed.item_name
        )
        
        rag_examples.append(rag_example)
    
    # Add to database
    ids = rag_service.add_examples_batch(rag_examples)
    
    print(f"Successfully added {len(ids)} examples to RAG database.")
    return len(ids)


if __name__ == "__main__":
    seed_rag_database()
