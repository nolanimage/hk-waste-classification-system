"""Classification orchestration service."""
from typing import Optional, Dict, Any, List
from app.services.openrouter import openrouter_service
from app.services.rag_service import rag_service
from app.services.embedding import embedding_service
from app.services.text_splitter import text_splitter_service
from app.services.image_detector import image_detector_service
from app.models.classification import (
    ClassificationResponse,
    ClassificationResult,
    MultiClassificationResponse
)
from app.models.rag import RAGExample
from app.config import settings


class ClassifierService:
    """Service for orchestrating the classification process."""
    
    async def classify(
        self,
        image_base64: Optional[str] = None,
        text: Optional[str] = None
    ) -> ClassificationResponse:
        """
        Classify an item using RAG and OpenRouter (single item, backward compatible).
        
        Args:
            image_base64: Base64 encoded image (optional)
            text: Text description (optional)
            
        Returns:
            ClassificationResponse with classification result
        """
        if not image_base64 and not text:
            raise ValueError("Either image or text must be provided")
        if image_base64 and text:
            raise ValueError("Please provide either image OR text, not both")
        
        # Step 1: Generate embedding for text input (if provided)
        text_embedding = None
        if text:
            text_embedding = embedding_service.generate_text_embedding(text)
        
        # Step 2: Retrieve similar examples from RAG
        similar_examples = rag_service.retrieve_similar(
            text=text,
            text_embedding=text_embedding
        )
        
        # Step 3: Call OpenRouter with examples
        classification_result = await openrouter_service.classify_item(
            image_base64=image_base64,
            text=text,
            examples=similar_examples
        )
        
        # Step 4: Format and return response
        return ClassificationResponse(
            item=classification_result.get("item", "Unknown item"),
            category=classification_result.get("category", "general"),
            bin=classification_result.get("bin", "General waste"),
            binColor=classification_result.get("binColor", "other"),
            explanation=classification_result.get("explanation", "Classification completed.")
        )
    
    async def classify_multiple(
        self,
        image_base64: Optional[str] = None,
        text: Optional[str] = None
    ) -> MultiClassificationResponse:
        """
        Classify multiple items from a single input.
        
        Args:
            image_base64: Base64 encoded image (optional)
            text: Text description (optional)
            
        Returns:
            MultiClassificationResponse with list of classification results
        """
        if not image_base64 and not text:
            raise ValueError("Either image or text must be provided")
        if image_base64 and text:
            raise ValueError("Please provide either image OR text, not both")
        
        input_type = "image" if image_base64 else "text"
        classification_results: List[ClassificationResult] = []
        
        if text:
            # Text input: split into multiple items
            item_descriptions = await text_splitter_service.split_items(text)
            
            if not item_descriptions:
                # Fallback to single item classification
                item_descriptions = [text]
            
            # Classify each item
            for item_text in item_descriptions:
                try:
                    # Generate embedding for this item
                    item_embedding = embedding_service.generate_text_embedding(item_text)
                    
                    # Retrieve similar examples
                    similar_examples = rag_service.retrieve_similar(
                        text=item_text,
                        text_embedding=item_embedding
                    )
                    
                    # Classify the item
                    classification_result = await openrouter_service.classify_item(
                        text=item_text,
                        examples=similar_examples
                    )
                    
                    result = ClassificationResult(
                        item=classification_result.get("item", "Unknown item"),
                        category=classification_result.get("category", "general"),
                        bin=classification_result.get("bin", "General waste"),
                        binColor=classification_result.get("binColor", "other"),
                        explanation=classification_result.get("explanation", "Classification completed."),
                        confidence=None,
                        bbox=None
                    )
                    
                    classification_results.append(result)
                    
                    # Auto-enrichment: Add high-confidence classifications to RAG database
                    self._auto_enrich_if_qualified(result, item_text)
                except Exception as e:
                    print(f"Error classifying item '{item_text}': {e}")
                    # Continue with other items
                    continue
        
        elif image_base64:
            # Image input: detect multiple objects
            detections = await image_detector_service.detect_objects(image_base64)
            
            if not detections:
                # Fallback to single item classification
                detections = [{"description": "item in image", "bbox": None, "mask": None, "confidence": 0.5}]
            
            # Get image size for cropping
            image_size = image_detector_service.get_image_size(image_base64)
            
            # Classify each detected object
            for detection in detections:
                try:
                    # Crop image if bounding box is available (with optional segmentation mask)
                    cropped_image = None
                    if detection.get("bbox"):
                        cropped_image = image_detector_service.crop_image(
                            image_base64,
                            detection["bbox"],
                            image_size,
                            mask=detection.get("mask")  # Pass segmentation mask if available
                        )
                    
                    # Use cropped image if available, otherwise use original
                    image_to_classify = cropped_image if cropped_image else image_base64
                    description = detection.get("description", "item in image")
                    
                    # Generate embedding for description
                    desc_embedding = embedding_service.generate_text_embedding(description)
                    
                    # Retrieve similar examples
                    similar_examples = rag_service.retrieve_similar(
                        text=description,
                        text_embedding=desc_embedding
                    )
                    
                    # Classify the item
                    classification_result = await openrouter_service.classify_item(
                        image_base64=image_to_classify,
                        text=description if not cropped_image else None,  # Use description only if no crop
                        examples=similar_examples
                    )
                    
                    result = ClassificationResult(
                        item=classification_result.get("item", "Unknown item"),
                        category=classification_result.get("category", "general"),
                        bin=classification_result.get("bin", "General waste"),
                        binColor=classification_result.get("binColor", "other"),
                        explanation=classification_result.get("explanation", "Classification completed."),
                        confidence=detection.get("confidence"),
                        bbox={"coordinates": detection.get("bbox")} if detection.get("bbox") else None,
                        mask={"coordinates": detection.get("mask")} if detection.get("mask") else None
                    )
                    
                    classification_results.append(result)
                    
                    # Auto-enrichment: Add high-confidence classifications to RAG database
                    self._auto_enrich_if_qualified(result, description)
                except Exception as e:
                    print(f"Error classifying detected object: {e}")
                    # Continue with other items
                    continue
        
        # If no results, return a default
        if not classification_results:
            classification_results.append(ClassificationResult(
                item="Unknown item",
                category="general",
                bin="General waste",
                binColor="other",
                explanation="No items could be classified.",
                confidence=None,
                bbox=None
            ))
        
        return MultiClassificationResponse(
            items=classification_results,
            total_items=len(classification_results),
            input_type=input_type
        )
    
    def _auto_enrich_if_qualified(
        self,
        result: ClassificationResult,
        description: str
    ) -> None:
        """
        Automatically add high-confidence classifications to RAG database.
        
        Args:
            result: Classification result
            description: Original text description or detected item description
        """
        # Check if auto-enrichment is enabled
        if not settings.AUTO_ENRICH_ENABLED:
            return
        
        # Check confidence threshold (if confidence is available)
        if result.confidence is not None:
            if result.confidence < settings.AUTO_ENRICH_CONFIDENCE_THRESHOLD:
                return  # Confidence too low, skip
        
        # Skip if item is too generic
        if result.item.lower() in ["unknown item", "item in image", "general waste"]:
            return
        
        # Skip if category is too generic
        if result.category.lower() == "general" and result.binColor == "other":
            return
        
        try:
            # Check for duplicates if enabled
            if settings.AUTO_ENRICH_CHECK_DUPLICATES:
                # Create a description for duplicate checking
                check_description = f"{result.item} - {description}".strip()
                if rag_service.check_duplicate(check_description, similarity_threshold=0.90):
                    print(f"Auto-enrichment: Skipping duplicate for '{result.item}'")
                    return
            
            # Generate embedding for the description
            text_description = f"{result.item} - {description}".strip()
            text_embedding = embedding_service.generate_text_embedding(text_description)
            
            # Create RAG example
            rag_example = RAGExample(
                item_name=result.item,
                text_description=text_description,
                text_embedding=text_embedding,
                category=result.category,
                bin_color=result.binColor,
                bin_type=result.bin,
                rules=result.explanation
            )
            
            # Add to database
            example_id = rag_service.add_example(rag_example)
            print(f"Auto-enrichment: Added '{result.item}' to RAG database (ID: {example_id})")
            
        except Exception as e:
            # Don't fail the classification if enrichment fails
            print(f"Auto-enrichment: Failed to add '{result.item}': {e}")


# Global instance
classifier_service = ClassifierService()
