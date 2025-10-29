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
            logger.info(f"Initializing Gemini model: {settings.GEMINI_MODEL}")
            # Use the stable API version
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=None,
                )
            )
            logger.info(f"Gemini model initialized successfully: {settings.GEMINI_MODEL}")
    
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
                
                # Handle different possible response formats
                response_text = None
                if hasattr(response, 'text'):
                    try:
                        response_text = response.text
                    except Exception:
                        # response.text might fail for complex responses
                        pass
                
                if not response_text and hasattr(response, 'candidates') and len(response.candidates) > 0:
                    # Alternative response format
                    response_text = response.candidates[0].content.parts[0].text
                elif not response_text and isinstance(response, str):
                    response_text = response
                
                if not response_text:
                    logger.error(f"Unable to extract text from Gemini API response")
                    logger.error(f"Response object type: {type(response)}")
                    raise ValueError("Unable to extract text from Gemini API response")
                
                logger.debug(f"Gemini response received, length: {len(response_text)} characters")
                results = self._parse_multiple_versions(response_text)
                
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
        if not response_text:
            logger.warning("Empty response text received from Gemini")
            return {
                "headings": ["Generated Heading A", "Generated Heading B"],
                "descriptions": ["Generated description content A.", "Generated description content B."]
            }
        
        logger.debug(f"Parsing response text, total length: {len(response_text)}")
        lines = response_text.strip().split('\n')
        logger.debug(f"Response has {len(lines)} lines")
        
        version_a_heading = ""
        version_a_description = ""
        version_b_heading = ""
        version_b_description = ""
        
        current_version = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            if line_stripped.upper().startswith("VERSION A"):
                current_version = "A"
                logger.debug("Found Version A marker")
                continue
            elif line_stripped.upper().startswith("VERSION B"):
                current_version = "B"
                logger.debug("Found Version B marker")
                continue
            elif line_stripped.upper().startswith("HEADING:"):
                heading = line_stripped.split("HEADING:", 1)[1].strip() if "HEADING:" in line_stripped.upper() else line_stripped.replace("HEADING:", "").strip()
                if current_version == "A":
                    version_a_heading = heading
                    logger.debug(f"Found Version A heading: {heading[:50]}...")
                elif current_version == "B":
                    version_b_heading = heading
                    logger.debug(f"Found Version B heading: {heading[:50]}...")
            elif line_stripped.upper().startswith("DESCRIPTION:"):
                description = line_stripped.split("DESCRIPTION:", 1)[1].strip() if "DESCRIPTION:" in line_stripped.upper() else line_stripped.replace("DESCRIPTION:", "").strip()
                if current_version == "A":
                    version_a_description = description
                    logger.debug(f"Found Version A description: {description[:50]}...")
                elif current_version == "B":
                    version_b_description = description
                    logger.debug(f"Found Version B description: {description[:50]}...")
        
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
            # Generate more distinct headings from input text
            input_words = input_text.split()
            
            if version == 0:
                # Version A: Extract first meaningful part, limit to reasonable length for social media
                # Take first ~60 words or until reasonable length (max 100 chars for headings)
                heading_parts = []
                current_length = 0
                max_length = 100
                
                for word in input_words:
                    if current_length + len(word) + 1 > max_length:
                        break
                    heading_parts.append(word)
                    current_length += len(word) + 1
                
                if heading_parts:
                    heading = " ".join(heading_parts)
                    # Don't add "..." if we have the full meaningful sentence
                    if len(input_text) > len(heading) + 20:
                        heading += "..."
                else:
                    # Fallback to first 100 chars if split fails
                    heading = input_text[:100].strip()
                description = "Lue lisää tästä aiheesta ja seuraa meitä päivittäin."
            else:
                # Version B: Create a different style heading (more engaging, question or statement format)
                # Extract key information but format differently
                if len(input_words) >= 4:
                    # Take key words, but format as a question or more engaging statement
                    # Get first 3-5 words for a punchier headline
                    key_words = input_words[:5]
                    heading = " ".join(key_words)
                    # Ensure it doesn't exceed limit
                    if len(heading) > 100:
                        heading = heading[:97] + "..."
                    # If it's very short, add context but keep it different from version A
                    if len(heading) < 30 and len(input_words) > 5:
                        heading = " ".join(input_words[:8])
                        if len(heading) > 100:
                            heading = heading[:97] + "..."
                else:
                    # For short input, add a prefix to make it distinct
                    heading = input_text[:95].strip()
                
                description = input_text
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