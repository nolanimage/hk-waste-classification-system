"""Admin API routes for managing RAG examples."""
from fastapi import APIRouter, HTTPException
from typing import List
from app.services.rag_service import rag_service
from app.services.embedding import embedding_service
from app.models.rag import RAGExample

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/add-example")
async def add_example(
    item_name: str,
    text_description: str,
    category: str,
    bin_color: str,
    bin_type: str,
    rules: str = None
):
    """
    Add a new classification example to the RAG database.
    
    Args:
        item_name: Name of the item
        text_description: Text description
        category: Item category
        bin_color: Bin color
        bin_type: Bin type description
        rules: Optional rules/notes
        
    Returns:
        ID of the added example
    """
    try:
        # Generate embedding
        text_embedding = embedding_service.generate_text_embedding(text_description)
        
        # Create RAG example
        example = RAGExample(
            item_name=item_name,
            text_description=text_description,
            text_embedding=text_embedding,
            category=category,
            bin_color=bin_color,
            bin_type=bin_type,
            rules=rules
        )
        
        # Add to database
        example_id = rag_service.add_example(example)
        
        return {"id": example_id, "message": "Example added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add example: {str(e)}")


@router.get("/examples")
async def get_all_examples():
    """Get all examples from the RAG database."""
    try:
        examples = rag_service.get_all_examples()
        return {"count": len(examples), "examples": examples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve examples: {str(e)}")
