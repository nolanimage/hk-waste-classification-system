"""OpenRouter API client for vision model calls."""
import httpx
import json
from typing import Optional, Dict, Any
from app.config import settings


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter service."""
        self.base_url = settings.openrouter_base_url
        self.headers = settings.openrouter_headers
        self.model = settings.VISION_MODEL
    
    async def classify_item(
        self,
        image_base64: Optional[str] = None,
        text: Optional[str] = None,
        examples: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Classify an item using OpenRouter vision model.
        
        Args:
            image_base64: Base64 encoded image (optional)
            text: Text description (optional)
            examples: List of similar examples from RAG (optional)
            
        Returns:
            Dictionary with classification result
        """
        if not image_base64 and not text:
            raise ValueError("Either image or text must be provided")
        
        # Build messages for the API
        messages = []
        
        # System message with Hong Kong rules
        system_prompt = self._build_system_prompt(examples)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # User message with image and/or text
        user_content = []
        
        if image_base64:
            # Ensure proper format
            if not image_base64.startswith("data:"):
                image_base64 = f"data:image/jpeg;base64,{image_base64}"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": image_base64}
            })
        
        if text:
            user_content.append({
                "type": "text",
                "text": f"Classify this item and consider any associated items (packaging, instructions, containers, etc.): {text}"
            })
        
        if not user_content:
            raise ValueError("Must provide either image or text")
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Choose model based on input type
        # Use vision model if image is provided, otherwise use text model
        from app.config import settings
        model_to_use = self.model if image_base64 else settings.TEXT_MODEL
        
        # Call OpenRouter API
        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": 0.3,
            "stream": False,  # Ensure we get complete response
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
                
                # Extract the classification from the response
                choice = result.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "")
                
                # If content is empty, check for refusal or try alternative fields
                if not content:
                    content = message.get("refusal") or message.get("reasoning") or ""
                    if not content:
                        # Log the full response for debugging
                        print(f"Warning: Empty response from OpenRouter. Full response: {result}")
                        # Try to get any text from the response
                        import json
                        content_str = json.dumps(result, indent=2)
                        print(f"Full response JSON: {content_str[:500]}")
                        # Return a fallback classification based on RAG examples if available
                        if examples and len(examples) > 0:
                            # Use the first similar example as fallback
                            first_example = examples[0]
                            return {
                                "item": first_example.get("item_name", "Unknown item"),
                                "category": first_example.get("category", "general"),
                                "bin": first_example.get("bin_type", "General waste"),
                                "binColor": first_example.get("bin_color", "other"),
                                "explanation": f"Classification based on similar example: {first_example.get('text_description', '')}"
                            }
                        raise ValueError("Empty response from OpenRouter API and no examples available")
                
                # Try to parse JSON from the response
                classification = self._parse_classification(content)
                return classification
                
        except httpx.HTTPError as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to classify item: {str(e)}")
    
    def _build_system_prompt(self, examples: Optional[list] = None) -> str:
        """Build the system prompt with Hong Kong rules and examples."""
        prompt = """You are a waste classification assistant for Hong Kong's waste management system, following official guidelines from the Environmental Protection Department (EPD).

Your task is to classify items and recommend the correct bin based on Hong Kong's official recycling system.

Reference: Official Hong Kong EPD guidelines - https://www.wastereduction.gov.hk/en-hk/recycling-tips

Hong Kong Waste Management System (Official EPD Guidelines):

THREE-COLOUR BINS (for source separation at source):
- BLUE BIN (Waste Paper): 
  * ACCEPTED: Clean and dry waste paper ONLY - newspapers, magazines, office paper, cardboard boxes, paper bags, envelopes, books (remove hard covers), paper packaging
  * NOT ACCEPTED: Wet/soiled paper, plastic-lined paper (e.g., coffee cups with plastic coating), composite materials, food containers with residue, thermal paper (receipts), laminated paper, paper with heavy ink/glue
  * REQUIREMENTS: Must be clean, dry, and free of food residue or contamination

- YELLOW BIN (Metal Cans):
  * ACCEPTED: Aluminum and metal cans ONLY (beverage cans, food cans). Must be empty, clean, and rinsed
  * NOT ACCEPTED: Other metal items (scrap metal, large metal objects, metal wires, metal utensils, metal containers that are not cans) - these should go to GREEN@COMMUNITY
  * REQUIREMENTS: Must be empty, clean, and preferably flattened to save space

- BROWN BIN (Plastic Bottles):
  * ACCEPTED: Plastic bottles ONLY (PET #1, HDPE #2 - usually with recycling symbols). Must be empty and clean
  * NOT ACCEPTED: Other plastic items (containers, bags, toys, styrofoam, plastic utensils, plastic packaging, plastic film) - these typically go to GREEN@COMMUNITY or general waste
  * REQUIREMENTS: Must be empty, clean, and rinsed. Remove caps/lids if they are different material (caps often go to general waste or GREEN@COMMUNITY)

GREEN@COMMUNITY (designated collection points - NOT the three-colour bins):
These are separate collection facilities, not the three-colour bins. Items include:
- Glass bottles and containers (must be clean and rinsed)
- Small electrical appliances and electronics (phones, chargers, small fans, etc.)
- Batteries (all types: rechargeable, single-use AA/AAA, car batteries)
- Beverage cartons (Tetra Pak, aseptic packaging)
- Fluorescent lamps and tubes
- Other recyclables not accepted in three-colour bins (e.g., other types of plastics, larger metal items, textiles)

OTHER CATEGORIES:
- FOOD WASTE: Organic waste, food scraps (if food waste collection is available in your area - check with building management)
- HAZARDOUS: Chemicals, medical waste, certain batteries (check with GREEN@COMMUNITY for specific guidelines)
- GENERAL WASTE: Non-recyclable items, contaminated items, items that don't fit other categories, items that cannot be cleaned

Important official rules (from EPD Clean Recycling Tips):
- Items for three-colour bins MUST be clean and dry - contamination can ruin entire batches
- Rinse containers before recycling (especially food containers)
- Remove labels, caps, and non-recyclable components when possible
- Contaminated items go to general waste - do not put contaminated items in recycling bins
- Many recyclables (glass, electronics, cartons, most plastics) require GREEN@COMMUNITY facilities, NOT the three-colour bins
- Composite materials (e.g., plastic-lined paper cups) should be separated if possible, otherwise often go to general waste
- When in doubt, check with your building management or visit a GREEN@COMMUNITY station
- Do not put items in plastic bags when placing in bins - place items directly in bins

You must respond with a JSON object in this exact format:
{
    "item": "item name",
    "category": "category (metal, plastic, paper, glass, organic, hazardous, general)",
    "bin": "specific bin description",
    "binColor": "blue, yellow, brown, green, other",
    "explanation": "brief explanation"
}
"""
        
        if examples:
            prompt += "\n\nSimilar examples from our database:\n"
            for i, ex in enumerate(examples[:5], 1):
                prompt += f"\nExample {i}:\n"
                prompt += f"  Item: {ex.get('item_name', 'Unknown')}\n"
                prompt += f"  Description: {ex.get('text_description', '')}\n"
                prompt += f"  Category: {ex.get('category', '')}\n"
                prompt += f"  Bin: {ex.get('bin_type', '')} ({ex.get('bin_color', '')})\n"
                if ex.get('rules'):
                    prompt += f"  Note: {ex.get('rules')}\n"
        
        prompt += "\n\nNow classify the user's item based on these rules and examples."
        
        return prompt
    
    def _parse_classification(self, content: str) -> Dict[str, Any]:
        """Parse classification from model response."""
        # Try to extract JSON from the response
        import re
        
        # Look for JSON object in the response
        json_match = re.search(r'\{[^{}]*"item"[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to parse the entire content as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Last resort: extract information using regex
        item_match = re.search(r'"item"\s*:\s*"([^"]+)"', content)
        category_match = re.search(r'"category"\s*:\s*"([^"]+)"', content)
        bin_match = re.search(r'"bin"\s*:\s*"([^"]+)"', content)
        bin_color_match = re.search(r'"binColor"\s*:\s*"([^"]+)"', content)
        explanation_match = re.search(r'"explanation"\s*:\s*"([^"]+)"', content)
        
        return {
            "item": item_match.group(1) if item_match else "Unknown item",
            "category": category_match.group(1) if category_match else "general",
            "bin": bin_match.group(1) if bin_match else "General waste",
            "binColor": bin_color_match.group(1) if bin_color_match else "other",
            "explanation": explanation_match.group(1) if explanation_match else content[:200]
        }


# Global instance
openrouter_service = OpenRouterService()
