"""Classification request and response models."""
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


class ClassificationRequest(BaseModel):
    """Request model for classification."""
    image: Optional[str] = Field(None, description="Base64 encoded image")
    text: Optional[str] = Field(None, description="Text description of the item")
    
    @model_validator(mode='after')
    def validate_input(self):
        """Validate that exactly one of image or text is provided."""
        has_image = self.image is not None and self.image.strip() != "" if isinstance(self.image, str) else self.image is not None
        has_text = self.text is not None and self.text.strip() != "" if isinstance(self.text, str) else self.text is not None
        
        if not has_image and not has_text:
            raise ValueError("Either image or text must be provided")
        if has_image and has_text:
            raise ValueError("Please provide either image OR text, not both")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "a crumpled soda can"
            }
        }


class ClassificationResult(BaseModel):
    """Single classification result for one item."""
    item: str = Field(..., description="Name of the item")
    category: str = Field(..., description="Category (e.g., metal, plastic, paper)")
    bin: str = Field(..., description="Bin type (e.g., yellow bin, blue bin)")
    binColor: str = Field(..., description="Bin color (blue, yellow, brown, other)")
    explanation: str = Field(..., description="Explanation of the classification")
    confidence: Optional[float] = Field(None, description="Confidence score for image detections")
    bbox: Optional[dict] = Field(None, description="Bounding box coordinates for image items")
    mask: Optional[dict] = Field(None, description="Segmentation mask coordinates (polygon) for precise object boundaries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item": "Aluminum soda can",
                "category": "metal",
                "bin": "Yellow bin (aluminum/metal cans)",
                "binColor": "yellow",
                "explanation": "This is an aluminum can, which should be placed in the yellow bin for metal recycling in Hong Kong.",
                "confidence": 0.95
            }
        }


class MultiClassificationResponse(BaseModel):
    """Response model for multiple item classifications."""
    items: List[ClassificationResult] = Field(..., description="List of classification results")
    total_items: int = Field(..., description="Total number of items detected")
    input_type: str = Field(..., description="Type of input: 'text' or 'image'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "item": "Aluminum soda can",
                        "category": "metal",
                        "bin": "Yellow bin (aluminum/metal cans)",
                        "binColor": "yellow",
                        "explanation": "Must be empty and clean."
                    },
                    {
                        "item": "Plastic water bottle",
                        "category": "plastic",
                        "bin": "Brown bin (plastic bottles)",
                        "binColor": "brown",
                        "explanation": "Must be empty and clean."
                    }
                ],
                "total_items": 2,
                "input_type": "text"
            }
        }


# Keep backward compatibility
ClassificationResponse = ClassificationResult
