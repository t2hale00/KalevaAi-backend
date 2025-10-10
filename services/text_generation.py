"""
Text generation service using Google Gemini API.
Generates headlines and descriptions for social media posts.
"""
import google.generativeai as genai
from typing import Dict, Optional
from loguru import logger

from config import settings


class TextGenerationService:
    """Service for generating text content using Gemini."""
    
    def __init__(self):
        """Initialize the Gemini API."""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured. Text generation will fail.")
            self.model = None
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_text(
        self,
        platform: str,
        content_type: str,
        text_length: str,
        input_text: Optional[str] = None,
        newspaper: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate heading and description for social media content.
        
        Args:
            platform: Target platform (instagram, facebook, linkedin)
            content_type: Content type (post, story)
            text_length: Desired text length (short, medium, long)
            input_text: Optional input text to base generation on
            newspaper: Regional newspaper brand
            
        Returns:
            Dictionary with 'heading' and 'description' keys
        """
        if not self.model:
            raise ValueError("Gemini API not configured. Please set GEMINI_API_KEY in .env file.")
        
        # Determine tone based on platform
        tone = "professional" if platform == "linkedin" else "friendly and engaging"
        
        # Build character limits based on Table 3
        heading_limits = self._get_heading_limits(platform, text_length)
        description_limits = self._get_description_limits(platform, content_type, text_length)
        
        # Build prompt
        prompt = self._build_prompt(
            platform=platform,
            content_type=content_type,
            tone=tone,
            heading_limits=heading_limits,
            description_limits=description_limits,
            input_text=input_text,
            newspaper=newspaper
        )
        
        logger.info(f"Generating text for {platform} {content_type} with {text_length} length")
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            logger.info("Text generation successful")
            return result
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def _get_heading_limits(self, platform: str, text_length: str) -> str:
        """Get character limits for headings based on platform."""
        limits = {
            "instagram": "≤100 characters",
            "facebook": "≤100 characters",
            "linkedin": "≤150 characters"
        }
        return limits.get(platform, "≤100 characters")
    
    def _get_description_limits(self, platform: str, content_type: str, text_length: str) -> str:
        """Get character limits for descriptions based on platform and length."""
        # Based on Table 3
        if content_type == "story":
            return "Not applicable for stories"
        
        limits = {
            "instagram": {
                "short": "≤100 characters",
                "medium": "100-500 characters",
                "long": "500-2200 characters"
            },
            "facebook": {
                "short": "≤100 characters",
                "medium": "100-1000 characters",
                "long": "1000-63206 characters"
            },
            "linkedin": {
                "short": "≤100 characters",
                "medium": "100-500 characters",
                "long": "500-3000 characters"
            }
        }
        
        return limits.get(platform, {}).get(text_length, "100-500 characters")
    
    def _build_prompt(
        self,
        platform: str,
        content_type: str,
        tone: str,
        heading_limits: str,
        description_limits: str,
        input_text: Optional[str],
        newspaper: Optional[str]
    ) -> str:
        """Build the prompt for Gemini."""
        base_context = f"""You are a social media content creator for {newspaper or 'Kaleva Media'}, a Finnish media company.
Generate compelling content for a {platform} {content_type}.

Tone: {tone}
Target audience: Finnish-speaking social media users

Requirements:
- Heading: {heading_limits}
- Description: {description_limits}
"""
        
        if input_text:
            base_context += f"\nBase your content on this input: {input_text}\n"
        
        base_context += """
Please generate:
1. A catchy heading/title
2. An engaging description/post copy

Format your response exactly as:
HEADING: [your heading here]
DESCRIPTION: [your description here]
"""
        
        return base_context
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse the Gemini response into heading and description."""
        lines = response_text.strip().split('\n')
        
        heading = ""
        description = ""
        
        for line in lines:
            if line.startswith("HEADING:"):
                heading = line.replace("HEADING:", "").strip()
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
        
        # If parsing fails, try to extract from the response
        if not heading or not description:
            # Fallback: use first line as heading, rest as description
            if lines:
                heading = lines[0].strip()
                description = " ".join(lines[1:]).strip() if len(lines) > 1 else ""
        
        return {
            "heading": heading or "Generated Heading",
            "description": description or "Generated description content."
        }


# Create singleton instance
text_generation_service = TextGenerationService()


