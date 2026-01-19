"""Image object detection service to detect and crop multiple objects."""
import base64
import json
import re
from typing import List, Dict, Tuple, Optional
from io import BytesIO
from PIL import Image
import httpx
from app.config import settings


class ImageDetectorService:
    """Service for detecting multiple objects in images."""
    
    def __init__(self):
        """Initialize image detector service."""
        self.base_url = settings.openrouter_base_url
        self.headers = settings.openrouter_headers
        self.model = settings.VISION_MODEL
    
    async def detect_objects(self, image_base64: str) -> List[Dict]:
        """
        Detect multiple objects in an image and return bounding boxes.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            List of dictionaries with 'bbox' (x, y, width, height) and 'description'
        """
        if not image_base64:
            return []
        
        # Ensure proper format
        if not image_base64.startswith("data:"):
            image_base64 = f"data:image/jpeg;base64,{image_base64}"
        
        try:
            detections = await self._detect_with_vision_model(image_base64)
            if detections:
                return detections
        except Exception as e:
            print(f"Vision model detection failed: {e}")
        
        # Fallback: assume single object
        return [{"bbox": None, "description": "item in image", "confidence": 0.5}]
    
    async def _detect_with_vision_model(self, image_base64: str) -> List[Dict]:
        """Use vision model to detect objects and get bounding boxes."""
        prompt = """Analyze this image and identify ALL waste items visible, including:
1. Items clearly visible in the image
2. Items that are part of or associated with visible items (packaging, labels, containers, etc.)
3. Items that are typically found together with the main items

For example:
- If you see a toy, also consider: packaging box, instruction manual, plastic wrapping
- If you see food, also consider: container, utensils, napkins, sauce packets
- If you see electronics, also consider: battery, charger, packaging, manuals

For each item, provide:
1. A brief description
2. Bounding box coordinates (x, y, width, height) as percentages of image dimensions (if visible)
3. Confidence level (0-1)

Return a JSON array with this format:
[
  {{
    "description": "item description",
    "bbox": [x_percent, y_percent, width_percent, height_percent],
    "confidence": 0.9
  }}
]

If you can't detect bounding boxes, return descriptions only. Include all associated items you can identify."""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a smart object detection assistant for waste classification. When you see an item, also identify associated items like packaging, labels, instructions, containers that typically come with it. Always return valid JSON arrays with item descriptions and bounding boxes."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_base64}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.3,
            "stream": False,
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    return []
                
                # Parse JSON array from response
                detections = self._parse_detections(content)
                return detections
                
        except Exception as e:
            print(f"Error in vision model detection: {e}")
            return []
    
    def _parse_detections(self, content: str) -> List[Dict]:
        """Parse detection results from model response."""
        # Try to find JSON array
        json_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if json_match:
            try:
                detections = json.loads(json_match.group())
                if isinstance(detections, list):
                    return detections
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Fallback: extract descriptions from text
        return self._extract_descriptions_fallback(content)
    
    def _extract_descriptions_fallback(self, content: str) -> List[Dict]:
        """Fallback: extract item descriptions from text response."""
        # Look for item descriptions in the text
        items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip JSON structure lines
            if line.startswith('{') or line.startswith('[') or line.startswith('}'):
                continue
            
            # Try to extract description
            desc_match = re.search(r'description["\']?\s*:\s*["\']?([^"\',}]+)', line, re.IGNORECASE)
            if desc_match:
                items.append({
                    "description": desc_match.group(1).strip(),
                    "bbox": None,
                    "confidence": 0.7
                })
            elif ':' in line and not line.startswith('http'):
                # Assume it's a description
                desc = line.split(':', 1)[1].strip().strip('"\'')
                if desc and len(desc) > 2:
                    items.append({
                        "description": desc,
                        "bbox": None,
                        "confidence": 0.6
                    })
        
        return items if items else [{"description": "item in image", "bbox": None, "confidence": 0.5}]
    
    def crop_image(self, image_base64: str, bbox: Optional[List[float]], image_size: Tuple[int, int]) -> Optional[str]:
        """
        Crop an image based on bounding box coordinates.
        
        Args:
            image_base64: Base64 encoded original image
            bbox: Bounding box as [x_percent, y_percent, width_percent, height_percent]
            image_size: (width, height) of original image
            
        Returns:
            Base64 encoded cropped image, or None if cropping fails
        """
        if not bbox or len(bbox) != 4:
            return None
        
        try:
            # Decode base64 image
            if image_base64.startswith("data:"):
                image_data = image_base64.split(",")[1]
            else:
                image_data = image_base64
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert percentage coordinates to pixels
            img_width, img_height = image.size
            x = int(bbox[0] * img_width / 100)
            y = int(bbox[1] * img_height / 100)
            width = int(bbox[2] * img_width / 100)
            height = int(bbox[3] * img_height / 100)
            
            # Ensure coordinates are within image bounds
            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))
            width = max(1, min(width, img_width - x))
            height = max(1, min(height, img_height - y))
            
            # Crop image
            cropped = image.crop((x, y, x + width, y + height))
            
            # Convert back to base64
            buffer = BytesIO()
            cropped.save(buffer, format="JPEG")
            cropped_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/jpeg;base64,{cropped_base64}"
            
        except Exception as e:
            print(f"Error cropping image: {e}")
            return None
    
    def get_image_size(self, image_base64: str) -> Tuple[int, int]:
        """Get the size of an image from base64 string."""
        try:
            if image_base64.startswith("data:"):
                image_data = image_base64.split(",")[1]
            else:
                image_data = image_base64
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            return image.size
        except Exception as e:
            print(f"Error getting image size: {e}")
            return (800, 600)  # Default size


# Global instance
image_detector_service = ImageDetectorService()
