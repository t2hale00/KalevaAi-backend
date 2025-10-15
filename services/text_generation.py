"""
Text generation service using Google Gemini API.
Generates headlines and descriptions for social media posts.
"""
import google.generativeai as genai
from typing import Dict, Optional
from loguru import logger

from config import settings
from services.prompt_manager import prompt_manager


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
        
        try:
            if self.model:
                # Try Gemini if available - generate both versions in one call
                prompt = prompt_manager.get_prompt(
                    platform=platform,
                    content_type=content_type,
                    text_length=text_length,
                    input_text=input_text,
                    newspaper=newspaper
                )
                
                response = self.model.generate_content(prompt)
                results = self._parse_multiple_versions(response.text)
                
                # Add both versions
                headings.extend(results["headings"])
                descriptions.extend(results["descriptions"])
                logger.info(f"Generated {len(results['headings'])} versions with Gemini")
            else:
                # Fallback to template-based generation
                for version in range(num_versions):
                    result = self._generate_fallback_text(platform, content_type, text_length, input_text, newspaper, version)
                    headings.append(result["heading"])
                    descriptions.append(result["description"])
                    logger.info(f"Generated version {version + 1} with fallback")
                    
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            # Use fallback if Gemini fails
            for version in range(num_versions):
                result = self._generate_fallback_text(platform, content_type, text_length, input_text, newspaper, version)
                headings.append(result["heading"])
                descriptions.append(result["description"])
                logger.info(f"Generated version {version + 1} with fallback after error")
        
        logger.info(f"Successfully generated {len(headings)} headings and {len(descriptions)} descriptions")
        return {
            "headings": headings,
            "descriptions": descriptions
        }
    
    def _parse_multiple_versions(self, response_text: str) -> Dict[str, list]:
        """Parse the Gemini response with Version A and Version B into separate headings and descriptions."""
        lines = response_text.strip().split('\n')
        
        version_a_heading = ""
        version_a_description = ""
        version_b_heading = ""
        version_b_description = ""
        
        current_version = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("VERSION A:"):
                current_version = "A"
                continue
            elif line.startswith("VERSION B:"):
                current_version = "B"
                continue
            elif line.startswith("HEADING:"):
                heading = line.replace("HEADING:", "").strip()
                if current_version == "A":
                    version_a_heading = heading
                elif current_version == "B":
                    version_b_heading = heading
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
                if current_version == "A":
                    version_a_description = description
                elif current_version == "B":
                    version_b_description = description
        
        # Fallback if parsing fails
        if not version_a_heading or not version_a_description:
            logger.warning("Failed to parse Version A, using fallback")
            version_a_heading = "Generated Heading A"
            version_a_description = "Generated description content A."
        
        if not version_b_heading or not version_b_description:
            logger.warning("Failed to parse Version B, using fallback")
            version_b_heading = "Generated Heading B"
            version_b_description = "Generated description content B."
        
        return {
            "headings": [version_a_heading, version_b_heading],
            "descriptions": [version_a_description, version_b_description]
        }
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse the Gemini response into heading and description."""
        lines = response_text.strip().split('\n')
        
        heading = ""
        description = ""
        
        # Look for Version A first (default), then Version B
        for line in lines:
            line = line.strip()
            if line.startswith("VERSION A:"):
                continue
            elif line.startswith("VERSION B:"):
                continue
            elif line.startswith("HEADING:"):
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
        
        # Note: Newspaper branding removed from headings as per user request
        
        return {
            "heading": heading,
            "description": description
        }


# Create singleton instance
text_generation_service = TextGenerationService()