"""Text splitting service to identify multiple items in text input."""
import json
import re
from typing import List
import httpx
from app.config import settings


class TextSplitterService:
    """Service for splitting text input into multiple item descriptions."""
    
    def __init__(self):
        """Initialize text splitter service."""
        self.base_url = settings.openrouter_base_url
        self.headers = settings.openrouter_headers
        # Use a more capable model for item detection
        # Check if ITEM_DETECTION_MODEL is set, otherwise use TEXT_MODEL
        if hasattr(settings, 'ITEM_DETECTION_MODEL') and settings.ITEM_DETECTION_MODEL:
            self.model = settings.ITEM_DETECTION_MODEL
        else:
            self.model = settings.TEXT_MODEL
        print(f"TextSplitter using model: {self.model}")
    
    async def split_items(self, text: str) -> List[str]:
        """
        Split text input into individual item descriptions.
        
        Args:
            text: Input text that may contain multiple items
            
        Returns:
            List of individual item descriptions
        """
        if not text or not text.strip():
            return []
        
        # First, try to use LLM to intelligently split items
        try:
            items = await self._split_with_llm(text)
            if items and len(items) > 1:
                # Successfully got multiple items from LLM
                return items
            elif items and len(items) == 1:
                # Got one item, try to expand it
                print(f"LLM returned single item, attempting expansion: {items[0]}")
                expanded = await self._expand_single_item(items[0])
                if expanded and len(expanded) > 1:
                    return expanded
                # If expansion failed, still return the single item (better than simple split)
                return items
        except Exception as e:
            print(f"LLM splitting failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to simple splitting only if LLM completely failed
        print("Falling back to simple splitting")
        return self._split_simple(text)
    
    async def _split_with_llm(self, text: str) -> List[str]:
        """Use LLM to intelligently identify multiple items, including associated items."""
        prompt = f"""Analyze this item: "{text}"

When disposing of "{text}", what SPECIFIC items are typically thrown away together? Think about:
- The main item itself
- Specific packaging (cardboard box, plastic bag, bubble wrap, etc.)
- Specific instructions (paper booklet, manual, etc.)
- Specific containers or materials that come with it

Return a JSON array with SPECIFIC item names, not generic categories.

EXAMPLES:
Input: "lego"
Output: ["lego pieces", "instruction booklet", "plastic packaging bags", "cardboard box"]

Input: "takeout food"
Output: ["food container", "plastic fork", "paper napkin", "sauce packet", "plastic bag"]

Input: "mobile phone"
Output: ["phone device", "battery", "charger cable", "cardboard packaging box", "instruction manual", "plastic wrapping"]

For "{text}", return a JSON array with at least 2-4 SPECIFIC items. Include the main item plus its associated materials.

JSON array:"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a smart waste classification assistant. You MUST identify ALL associated items when analyzing waste. When someone says 'lego', you MUST identify: lego pieces, instruction booklets (paper), plastic packaging, cardboard box. When someone says 'takeout', identify: container, utensils, napkins, sauce packets. ALWAYS think about packaging, instructions, containers, labels. ALWAYS return a JSON array with multiple items (minimum 2-4 items). Never return just the single input item."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,  # Higher temperature for more creative/expansive thinking
            "stream": False,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    print("Warning: Empty response from LLM")
                    return []
                
                # Debug: print raw response (truncated for logs)
                print(f"Raw LLM response (first 500 chars): {content[:500]}")
                
                # Try to extract JSON array from response
                items = self._parse_json_array(content)
                print(f"Parsed items (first attempt): {items}, count: {len(items) if items else 0}")
                
                if items and len(items) > 0:
                    # Clean and normalize items
                    cleaned = [self._clean_item(item) for item in items if item and item.strip()]
                    print(f"Cleaned items: {cleaned}, count: {len(cleaned)}")
                    
                    if len(cleaned) > 1:
                        print(f"✓ Successfully detected {len(cleaned)} items: {cleaned}")
                        return cleaned
                    elif len(cleaned) == 1:
                        # Only one item - try to expand it
                        print(f"Only one item detected, expanding: {cleaned[0]}")
                        expanded = await self._expand_single_item(cleaned[0])
                        if expanded and len(expanded) > 1:
                            print(f"✓ Expanded to {len(expanded)} items: {expanded}")
                            return expanded
                        print(f"Expansion failed or returned single item, returning: {cleaned}")
                        return cleaned
                
                # If parsing failed, try alternative parsing
                print(f"Warning: Standard parsing failed, trying alternative methods")
                items = self._parse_json_array_alternative(content)
                if items and len(items) > 1:
                    cleaned = [self._clean_item(item) for item in items if item and item.strip()]
                    print(f"✓ Alternative parsing found {len(cleaned)} items: {cleaned}")
                    return cleaned
                
                print(f"Warning: Could not parse items from response")
                return []
        except Exception as e:
            print(f"Error in LLM splitting: {e}")
            return []
    
    def _parse_json_array(self, content: str) -> List[str]:
        """Parse JSON array from LLM response."""
        # Clean the content first
        content = content.strip()
        
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        # Try to find JSON array - use a more robust pattern
        # First try: find complete JSON array (handles nested structures better)
        patterns = [
            r'\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\]',  # Nested arrays
            r'\[.*?\]',  # Simple array
        ]
        
        for pattern in patterns:
            json_match = re.search(pattern, content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed
                except json.JSONDecodeError as e:
                    continue
        
        # Try parsing the entire content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Last resort: extract quoted strings
        quoted_items = re.findall(r'["\']([^"\']+)["\']', content)
        if quoted_items and len(quoted_items) > 1:
            return quoted_items
        
        return []
    
    def _parse_json_array_alternative(self, content: str) -> List[str]:
        """Alternative parsing method for JSON arrays."""
        # Look for items in quotes
        items = re.findall(r'["\']([^"\']+)["\']', content)
        if items and len(items) > 1:
            return items
        
        # Look for items after colons or dashes
        lines = content.split('\n')
        items = []
        for line in lines:
            # Match patterns like: "item", - item, 1. item, etc.
            match = re.search(r'["\']([^"\']+)["\']|[-•]\s*([^\n,]+)|^\d+\.\s*([^\n,]+)', line, re.IGNORECASE)
            if match:
                item = match.group(1) or match.group(2) or match.group(3)
                if item and item.strip():
                    items.append(item.strip())
        
        return items if len(items) > 1 else []
    
    def _split_simple(self, text: str) -> List[str]:
        """Simple fallback splitting using common delimiters."""
        # Common patterns for multiple items
        # "a can, a bottle, and a newspaper"
        # "can, bottle, newspaper"
        # "three items: can, bottle, newspaper"
        
        # Remove common prefixes
        text = re.sub(r'^(i have|there are|items?:\s*)', '', text, flags=re.IGNORECASE)
        
        # Split by common delimiters
        items = re.split(r'[,;]|\sand\s', text, flags=re.IGNORECASE)
        
        # Clean each item
        cleaned_items = []
        for item in items:
            cleaned = self._clean_item(item)
            if cleaned:
                cleaned_items.append(cleaned)
        
        # If we only got one item, return it
        if len(cleaned_items) <= 1:
            return [text.strip()] if text.strip() else []
        
        return cleaned_items
    
    async def _expand_single_item(self, item: str) -> List[str]:
        """Try to expand a single item into multiple associated items."""
        if not item or len(item) < 2:
            return []
        
        expand_prompt = f"""The user mentioned: "{item}"

When disposing of this item, what other items are typically thrown away with it? Think about:
- Packaging materials (boxes, bags, wrapping)
- Instructions or manuals (paper)
- Containers or holders
- Labels or tags
- Other associated materials

Return a JSON array with at least 2-4 items including the main item and its associated items.

Example: If input is "toy", return: ["toy", "cardboard box", "instruction manual", "plastic packaging"]

Return JSON array:"""
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You identify associated waste items. Always return JSON arrays with multiple items."
                    },
                    {
                        "role": "user",
                        "content": expand_prompt
                    }
                ],
                "temperature": 0.5,
                "stream": False,
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    items = self._parse_json_array(content)
                    if items and len(items) > 1:
                        return [self._clean_item(item) for item in items if item and item.strip()]
        except Exception as e:
            print(f"Error expanding item: {e}")
        
        return []
    
    def _clean_item(self, item: str) -> str:
        """Clean and normalize an item description."""
        if not item:
            return ""
        
        # Remove leading/trailing whitespace
        item = item.strip()
        
        # Remove common prefixes
        item = re.sub(r'^(a|an|the)\s+', '', item, flags=re.IGNORECASE)
        
        # Remove numbers and ordinals at the start
        item = re.sub(r'^\d+\s*(st|nd|rd|th)?\s*', '', item, flags=re.IGNORECASE)
        
        return item.strip()


# Global instance
text_splitter_service = TextSplitterService()
