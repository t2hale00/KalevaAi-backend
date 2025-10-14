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
            # Use the stable API version
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
    
    def generate_text(
        self,
        platform: str,
        content_type: str,
        text_length: str,
        input_text: Optional[str] = None,
        newspaper: Optional[str] = None,
        num_versions: int = 2
    ) -> Dict[str, list]:
        """
        Generate heading and description for social media content.
        
        Args:
            platform: Target platform (instagram, facebook, linkedin)
            content_type: Content type (post, story)
            text_length: Desired text length (short, medium, long)
            input_text: Optional input text to base generation on
            newspaper: Regional newspaper brand
            
        Returns:
            Dictionary with 'headings' and 'descriptions' keys (lists of versions)
        """
        # Generate multiple versions of text
        logger.info(f"Generating {num_versions} versions of text for {platform} {content_type} with {text_length} length")
        
        headings = []
        descriptions = []
        
        for version in range(num_versions):
            try:
                if self.model:
                    # Try Gemini if available
                    tone = "professional" if platform == "linkedin" else "friendly and engaging"
                    heading_limits = self._get_heading_limits(platform, text_length)
                    description_limits = self._get_description_limits(platform, content_type, text_length)
                    
                    prompt = self._build_prompt(
                        platform=platform,
                        content_type=content_type,
                        tone=tone,
                        heading_limits=heading_limits,
                        description_limits=description_limits,
                        input_text=input_text,
                        newspaper=newspaper
                    )
                    # Add version variation to prompt
                    if version > 0:
                        prompt += f"\n\nGenerate a different variation (version {version + 1}) with alternative wording and style."
                    
                    response = self.model.generate_content(prompt)
                    result = self._parse_response(response.text)
                    headings.append(result["heading"])
                    descriptions.append(result["description"])
                    logger.info(f"Generated version {version + 1} with Gemini")
                else:
                    # Fallback to template-based generation
                    result = self._generate_fallback_text(platform, content_type, text_length, input_text, newspaper, version)
                    headings.append(result["heading"])
                    descriptions.append(result["description"])
                    logger.info(f"Generated version {version + 1} with fallback")
                    
            except Exception as e:
                logger.error(f"Error generating text version {version + 1}: {str(e)}")
                # Use fallback if Gemini fails
                result = self._generate_fallback_text(platform, content_type, text_length, input_text, newspaper, version)
                headings.append(result["heading"])
                descriptions.append(result["description"])
                logger.info(f"Generated version {version + 1} with fallback after error")
        
        logger.info(f"Successfully generated {len(headings)} headings and {len(descriptions)} descriptions")
        return {
            "headings": headings,
            "descriptions": descriptions
        }
    
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
    
    def _generate_fallback_text(
        self,
        platform: str,
        content_type: str,
        text_length: str,
        input_text: Optional[str],
        newspaper: Optional[str],
        version: int = 0
    ) -> Dict[str, str]:
        """Generate fallback text using templates when Gemini is not available."""
        
        # Base templates with multiple versions
        templates = {
            "instagram": [
                {
                    "heading": "Tiedä, mitä äänellesi tapahtuu",
                    "description": "Lue uusimmat uutiset ja seuraa tapahtumia meidän kanssasi. Jaa mielipiteesi ja ota osaa keskusteluun."
                },
                {
                    "heading": "Pysy ajan tasalla tapahtumista",
                    "description": "Seuraa paikallisia uutisia ja tapahtumia. Ota osaa yhteisöömme ja jaa ajatuksiasi kanssamme."
                }
            ],
            "facebook": [
                {
                    "heading": "Seuraa meitä päivittäin",
                    "description": "Pysy ajan tasalla uusimmista uutisista ja tapahtumista. Liity yhteisöömme ja jaa ajatuksiasi kanssamme."
                },
                {
                    "heading": "Liity keskusteluun kanssamme",
                    "description": "Lue viimeisimmät uutiset ja ota osaa yhteisöömme. Jaa mielipiteesi ja keskustele aiheista."
                }
            ],
            "linkedin": [
                {
                    "heading": "Ammattitaitoista journalismia",
                    "description": "Lue syvällisiä analyysejä ja ammattitaitoista journalismia. Pysy ajan tasalla alasi viimeisimmistä kehityksistä."
                },
                {
                    "heading": "Syvällistä asiantuntemusta",
                    "description": "Saat ajantasaiset uutiset ja ammattitaitoista näkökulmaa. Seuraa alasi kehitystä kanssamme."
                }
            ]
        }
        
        # Get base template for this version
        platform_templates = templates.get(platform, templates["instagram"])
        template_index = version % len(platform_templates)
        base_template = platform_templates[template_index]
        
        # Customize based on input text
        if input_text:
            # Use input text as inspiration with version variation
            if version == 0:
                heading = f"{input_text[:50]}..."
                description = f"Lue lisää aiheesta: {input_text}"
            else:
                heading = f"Tietoa aiheesta: {input_text[:40]}"
                description = f"Tutustu aiheeseen: {input_text}"
        else:
            heading = base_template["heading"]
            description = base_template["description"]
        
        # Add newspaper branding
        if newspaper:
            heading = f"{newspaper}: {heading}"
        
        return {
            "heading": heading,
            "description": description
        }


# Create singleton instance
text_generation_service = TextGenerationService()


