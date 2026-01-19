"""Image object detection service to detect and crop multiple objects with optional segmentation support.

Note: Segmentation is optional and primarily used for irregular shapes. Bounding boxes work well
for most waste items. The system handles mismatches between detection and segmentation gracefully.
"""
import base64
import json
import re
from typing import List, Dict, Tuple, Optional
from io import BytesIO
from PIL import Image, ImageDraw
import httpx
from app.config import settings


class ImageDetectorService:
    """Service for detecting multiple objects in images."""
    
    def __init__(self):
        """Initialize image detector service."""
        self.base_url = settings.openrouter_base_url
        self.headers = settings.openrouter_headers
        self.model = settings.VISION_MODEL
    
    async def detect_objects(self, image_base64: str, use_segmentation: bool = False) -> List[Dict]:
        """
        Detect multiple objects in an image with optional segmentation masks.
        
        Note: Segmentation is optional and may not always be available. The system works
        primarily with bounding boxes. Masks are used as an enhancement when available.
        
        Args:
            image_base64: Base64 encoded image
            use_segmentation: Whether to request segmentation masks (default: False)
                            Set to True only if you need precise boundaries for irregular shapes.
                            Most cases work fine with bounding boxes alone.
            
        Returns:
            List of dictionaries with 'bbox', 'mask' (optional), 'description', and 'confidence'
            - If mask is None, the system uses bounding box for cropping
            - If mask is provided, it's used for more precise object isolation
        """
        if not image_base64:
            return []
        
        # Ensure proper format
        if not image_base64.startswith("data:"):
            image_base64 = f"data:image/jpeg;base64,{image_base64}"
        
        try:
            detections = await self._detect_with_vision_model(image_base64, use_segmentation)
            if detections:
                return detections
        except Exception as e:
            print(f"Vision model detection failed: {e}")
        
        # Fallback: assume single object
        return [{"bbox": None, "mask": None, "description": "item in image", "confidence": 0.5}]
    
    async def _detect_with_vision_model(self, image_base64: str, use_segmentation: bool = False) -> List[Dict]:
        """Use vision model to detect objects with bounding boxes and optional segmentation masks."""
        if use_segmentation:
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
2. Bounding box coordinates (x, y, width, height) as percentages of image dimensions
3. Segmentation mask coordinates (optional): Array of [x, y] pixel coordinates that outline the object boundary
4. Confidence level (0-1)

Return a JSON array with this format:
[
  {{
    "description": "item description",
    "bbox": [x_percent, y_percent, width_percent, height_percent],
    "mask": [[x1, y1], [x2, y2], ...] or null if not available,
    "confidence": 0.9
  }}
]

IMPORTANT: 
- Always provide a bounding box (bbox) for each item
- Mask is optional - only provide if you can accurately segment the object
- If you detect an item but cannot provide a mask, set mask to null
- The number of items you detect should match the number of entries in the array
- Each entry must have at least a description and bbox

The mask should be an array of [x, y] coordinate pairs (as percentages 0-100) that form a polygon outlining the object. Include all associated items you can identify."""
        else:
            prompt = """Analyze this image and identify ALL waste items visible, including:
1. Items clearly visible in the image
2. Items that are part of or associated with visible items (packaging, labels, containers, etc.)
3. Items that are typically found together with the main items

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
                    "content": "You are a smart object detection assistant for waste classification. When you see an item, also identify associated items like packaging, labels, instructions, containers that typically come with it. Always return valid JSON arrays with item descriptions and bounding boxes. Be consistent: the number of items you describe should match the number of entries in your response."
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
        """
        Parse detection results from model response, including segmentation masks.
        
        Handles mismatches gracefully:
        - If detection has bbox but no mask: uses bbox (normal case)
        - If detection has mask but no bbox: generates bbox from mask bounds
        - If detection has description but no bbox/mask: uses description only
        - Ensures all detections are normalized with consistent structure
        """
        # Try to find JSON array
        json_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if json_match:
            try:
                detections = json.loads(json_match.group())
                if isinstance(detections, list):
                    return self._normalize_detections(detections)
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return self._normalize_detections(parsed)
        except json.JSONDecodeError:
            pass
        
        # Fallback: extract descriptions from text
        return self._extract_descriptions_fallback(content)
    
    def _normalize_detections(self, detections: List[Dict]) -> List[Dict]:
        """
        Normalize detection results to handle mismatches between detection and segmentation.
        
        Ensures:
        - All detections have required fields
        - Handles cases where mask exists but bbox doesn't (generates bbox from mask)
        - Handles cases where bbox exists but mask doesn't (mask is optional)
        - Handles cases where only description exists (bbox/mask are optional)
        """
        normalized = []
        for detection in detections:
            normalized_det = {
                "description": detection.get("description", "item in image"),
                "bbox": detection.get("bbox"),
                "mask": detection.get("mask"),
                "confidence": detection.get("confidence", 0.5)
            }
            
            # Handle mismatch: if mask exists but no bbox, generate bbox from mask
            if normalized_det["mask"] and not normalized_det["bbox"]:
                mask_coords = normalized_det["mask"]
                if mask_coords and len(mask_coords) > 0:
                    try:
                        # Extract x and y coordinates
                        xs = []
                        ys = []
                        for coord in mask_coords:
                            if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                xs.append(float(coord[0]))
                                ys.append(float(coord[1]))
                        
                        if xs and ys:
                            x_min, x_max = min(xs), max(xs)
                            y_min, y_max = min(ys), max(ys)
                            normalized_det["bbox"] = [
                                x_min, y_min, 
                                x_max - x_min, 
                                y_max - y_min
                            ]
                    except (ValueError, TypeError, IndexError) as e:
                        print(f"Warning: Could not generate bbox from mask: {e}")
                        # Keep mask but no bbox - will use full image for this detection
            
            # Validate bbox format if present
            if normalized_det["bbox"]:
                if not isinstance(normalized_det["bbox"], list) or len(normalized_det["bbox"]) != 4:
                    print(f"Warning: Invalid bbox format, setting to None: {normalized_det['bbox']}")
                    normalized_det["bbox"] = None
            
            # Validate mask format if present
            if normalized_det["mask"]:
                if not isinstance(normalized_det["mask"], list):
                    print(f"Warning: Invalid mask format, setting to None: {normalized_det['mask']}")
                    normalized_det["mask"] = None
            
            normalized.append(normalized_det)
        
        return normalized
    
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
                    "mask": None,
                    "confidence": 0.7
                })
            elif ':' in line and not line.startswith('http'):
                # Assume it's a description
                desc = line.split(':', 1)[1].strip().strip('"\'')
                if desc and len(desc) > 2:
                    items.append({
                        "description": desc,
                        "bbox": None,
                        "mask": None,
                        "confidence": 0.6
                    })
        
        return items if items else [{"description": "item in image", "bbox": None, "mask": None, "confidence": 0.5}]
    
    def crop_image(
        self, 
        image_base64: str, 
        bbox: Optional[List[float]], 
        image_size: Tuple[int, int],
        mask: Optional[List[List[float]]] = None
    ) -> Optional[str]:
        """
        Crop an image based on bounding box or segmentation mask.
        
        Args:
            image_base64: Base64 encoded original image
            bbox: Bounding box as [x_percent, y_percent, width_percent, height_percent]
            image_size: (width, height) of original image
            mask: Optional segmentation mask as list of [x, y] coordinate pairs (percentages)
            
        Returns:
            Base64 encoded cropped image with mask applied, or None if cropping fails
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
            
            # If mask is available, use it for precise cropping
            if mask and len(mask) > 0:
                try:
                    # Convert mask coordinates from percentages to pixels
                    mask_pixels = [
                        (int(coord[0] * img_width / 100), int(coord[1] * img_height / 100))
                        for coord in mask
                        if isinstance(coord, (list, tuple)) and len(coord) >= 2
                    ]
                    
                    if len(mask_pixels) >= 3:  # Need at least 3 points for a polygon
                        # Create a mask image
                        mask_img = Image.new('L', (img_width, img_height), 0)
                        ImageDraw.Draw(mask_img).polygon(mask_pixels, fill=255)
                        
                        # Apply mask to image
                        if image.mode == 'RGBA':
                            # Create alpha channel from mask
                            alpha = image.split()[3]
                            alpha = Image.composite(alpha, Image.new('L', image.size, 0), mask_img)
                            image.putalpha(alpha)
                        else:
                            # Convert to RGBA and apply mask
                            image = image.convert('RGBA')
                            alpha = Image.new('L', image.size, 255)
                            alpha = Image.composite(alpha, Image.new('L', image.size, 0), mask_img)
                            image.putalpha(alpha)
                except Exception as e:
                    print(f"Warning: Could not apply mask, using bbox only: {e}")
                    # Fall through to standard crop
            
            # Crop to bounding box (with mask applied if available)
            cropped = image.crop((x, y, x + width, y + height))
            
            # Convert back to base64 (preserve transparency if mask was used)
            buffer = BytesIO()
            if cropped.mode == 'RGBA':
                # Save as PNG to preserve transparency
                cropped.save(buffer, format="PNG")
                cropped_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return f"data:image/png;base64,{cropped_base64}"
            else:
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
