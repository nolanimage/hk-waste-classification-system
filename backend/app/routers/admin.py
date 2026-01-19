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


@router.get("/statistics")
async def get_statistics():
    """
    Get statistics about items in the RAG database.
    Returns common items grouped by category and bin type.
    """
    try:
        examples = rag_service.get_all_examples()
        
        # Group by category
        by_category = {}
        by_bin_color = {}
        by_bin_type = {}
        all_items = []
        
        for example in examples:
            category = example.get("category", "general")
            bin_color = example.get("bin_color", "other")
            bin_type = example.get("bin_type", "General waste")
            item_name = example.get("item_name", "Unknown")
            
            # Group by category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item_name)
            
            # Group by bin color
            if bin_color not in by_bin_color:
                by_bin_color[bin_color] = []
            by_bin_color[bin_color].append(item_name)
            
            # Group by bin type
            if bin_type not in by_bin_type:
                by_bin_type[bin_type] = []
            by_bin_type[bin_type].append(item_name)
            
            all_items.append(item_name)
        
        # Remove duplicates and sort
        for key in by_category:
            by_category[key] = sorted(list(set(by_category[key])))
        for key in by_bin_color:
            by_bin_color[key] = sorted(list(set(by_bin_color[key])))
        for key in by_bin_type:
            by_bin_type[key] = sorted(list(set(by_bin_type[key])))
        all_items = sorted(list(set(all_items)))
        
        return {
            "total_examples": len(examples),
            "unique_items": len(all_items),
            "by_category": by_category,
            "by_bin_color": by_bin_color,
            "by_bin_type": by_bin_type,
            "all_items": all_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")
