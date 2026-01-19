"""Content filtering service to validate and filter inappropriate inputs."""
import re
from typing import Optional, Tuple


class ContentFilterService:
    """Service for filtering inappropriate content from user inputs."""
    
    # Inappropriate keywords (case-insensitive)
    INAPPROPRIATE_KEYWORDS = [
        # Human/body parts
        r'\b(human|person|people|body|face|head|hand|foot|leg|arm|breast|genital|penis|vagina)\b',
        # Sexual content
        r'\b(sex|sexual|porn|nude|naked|erotic|xxx|adult|explicit)\b',
        # Violence
        r'\b(violence|weapon|gun|knife|blood|kill|murder)\b',
        # Drugs
        r'\b(drug|cocaine|heroin|marijuana|cannabis|opium)\b',
    ]
    
    # Waste-related keywords that should be allowed (to avoid false positives)
    ALLOWED_WASTE_KEYWORDS = [
        'bottle', 'can', 'container', 'paper', 'plastic', 'metal', 'glass',
        'cardboard', 'newspaper', 'magazine', 'battery', 'electronics',
        'food', 'waste', 'trash', 'recycle', 'recycling', 'bin'
    ]
    
    def __init__(self):
        """Initialize content filter."""
        # Compile regex patterns
        self.inappropriate_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.INAPPROPRIATE_KEYWORDS
        ]
    
    def validate_input(
        self, 
        text: Optional[str] = None, 
        image_base64: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate input content and filter inappropriate material.
        
        Args:
            text: Text input to validate
            image_base64: Image input (base64) - basic validation only
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if content is appropriate
            - error_message: Error message if invalid, None if valid
        """
        # Validate text input
        if text:
            is_valid, error = self._validate_text(text)
            if not is_valid:
                return False, error
        
        # Basic image validation (size, format)
        if image_base64:
            is_valid, error = self._validate_image(image_base64)
            if not is_valid:
                return False, error
        
        return True, None
    
    def _validate_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate text content for appropriateness.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Text input cannot be empty"
        
        # Check length
        if len(text) > 1000:
            return False, "Text input is too long (max 1000 characters)"
        
        # Check for inappropriate content
        text_lower = text.lower()
        
        # Check against inappropriate patterns
        for pattern in self.inappropriate_patterns:
            if pattern.search(text):
                # Check if it's a false positive (waste-related context)
                if not self._is_waste_related(text):
                    return False, "Input contains inappropriate content. Please describe waste items only."
        
        # Check if input is actually about waste items
        if not self._is_waste_related(text):
            return False, "Please describe waste items or recyclable materials only. This system is for waste classification."
        
        return True, None
    
    def _is_waste_related(self, text: str) -> bool:
        """
        Check if text is related to waste/recycling items.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be about waste items
        """
        text_lower = text.lower()
        
        # First, check if it contains inappropriate keywords that should NEVER be allowed
        # even if they might seem waste-related
        strong_block_patterns = [
            r'\b(human|person|people)\s+(body|corpse|cadaver)\b',
            r'\b(body|corpse|cadaver)\s+(bag|container)\b',
        ]
        for pattern in strong_block_patterns:
            if re.search(pattern, text_lower):
                return False  # Never allow these, even if they contain waste keywords
        
        # Check for waste-related keywords (including non-recyclable items)
        waste_keywords = [
            'waste', 'trash', 'garbage', 'recycle', 'recycling', 'bin',
            'bottle', 'can', 'container', 'paper', 'plastic', 'metal',
            'glass', 'cardboard', 'newspaper', 'magazine', 'battery',
            'electronics', 'food', 'item', 'object', 'material', 'dispose',
            'throw', 'discard', 'recyclable', 'disposal', 'general waste',
            'styrofoam', 'foam', 'contaminated', 'dirty', 'soiled', 'used',
            'broken', 'damaged', 'non-recyclable', 'unrecyclable', 'cup',
            'bag', 'wrapper', 'packaging', 'takeout', 'disposable'
        ]
        
        # If text contains waste-related keywords, likely valid
        for keyword in waste_keywords:
            if keyword in text_lower:
                return True
        
        # Check for common item descriptions
        item_patterns = [
            r'\b(a|an|the)\s+\w+\s+(can|bottle|container|box|bag|item|object)\b',
            r'\b(empty|used|old|broken|waste|recyclable)\s+\w+',
            r'\b\w+\s+(for|to)\s+(recycle|dispose|throw|discard)',
        ]
        
        for pattern in item_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # If text is very short and doesn't contain waste keywords, not waste-related
        if len(text.split()) < 3:
            return False
        
        # If no waste keywords found, it's likely not waste-related
        # Be more strict - default to False if uncertain
        return False
    
    def _validate_image(self, image_base64: str) -> Tuple[bool, Optional[str]]:
        """
        Basic image validation (format, size).
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not image_base64:
            return False, "Image cannot be empty"
        
        # Check if it's a valid base64 string
        try:
            # Remove data URL prefix if present
            if image_base64.startswith("data:"):
                image_data = image_base64.split(",")[1]
            else:
                image_data = image_base64
            
            # Decode to check if valid base64
            import base64
            decoded = base64.b64decode(image_data, validate=True)
            
            # Check size (max 10MB)
            if len(decoded) > 10 * 1024 * 1024:
                return False, "Image is too large (max 10MB)"
            
            # Check if it's a valid image format (basic check)
            # More thorough validation would require PIL/opencv
            if len(decoded) < 100:
                return False, "Image appears to be invalid or corrupted"
            
        except Exception as e:
            return False, f"Invalid image format: {str(e)}"
        
        return True, None
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input by removing potentially problematic content.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues (keep basic punctuation)
        # Keep: letters, numbers, spaces, basic punctuation
        text = re.sub(r'[^\w\s\.,!?\-]', '', text)
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()


# Global instance
content_filter_service = ContentFilterService()
