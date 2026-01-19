"""Classification API routes."""
from fastapi import APIRouter, HTTPException
from app.models.classification import (
    ClassificationRequest,
    ClassificationResponse,
    MultiClassificationResponse
)
from app.services.classifier import classifier_service
from app.services.content_filter import content_filter_service

router = APIRouter(prefix="/api", tags=["classification"])


@router.post("/classify", response_model=MultiClassificationResponse)
async def classify_item(request: ClassificationRequest) -> MultiClassificationResponse:
    """
    Classify waste items from image OR text input (not both).
    Supports multiple item detection and classification.
    
    Args:
        request: ClassificationRequest with image (base64) OR text
        
    Returns:
        MultiClassificationResponse with list of classification results
    """
    # Validate that exactly one input is provided
    has_image = request.image is not None and (isinstance(request.image, str) and len(request.image.strip()) > 0)
    has_text = request.text is not None and (isinstance(request.text, str) and len(request.text.strip()) > 0)
    
    if not has_image and not has_text:
        raise HTTPException(status_code=400, detail="Either image or text must be provided")
    if has_image and has_text:
        raise HTTPException(status_code=400, detail="Please provide either image OR text, not both")
    
    # Content filtering: Validate input for appropriateness
    is_valid, error_message = content_filter_service.validate_input(
        text=request.text if has_text else None,
        image_base64=request.image if has_image else None
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message or "Invalid input content")
    
    # Sanitize text input if provided
    sanitized_text = None
    if has_text and request.text:
        sanitized_text = content_filter_service.sanitize_text(request.text)
    
    try:
        result = await classifier_service.classify_multiple(
            image_base64=request.image if has_image else None,
            text=sanitized_text if has_text else None
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
