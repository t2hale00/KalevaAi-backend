"""
Prompt Manager Service for loading and managing platform-specific prompts.
Centralizes all prompt loading and provides a clean interface for text generation.
"""
from typing import Dict, Optional
from pathlib import Path
from loguru import logger
import importlib.util

class PromptManager:
    """Manages loading and accessing platform-specific prompts."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self._loaded_prompts = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompt modules from the prompts directory."""
        platforms = ["instagram", "facebook", "linkedin"]
        
        for platform in platforms:
            platform_dir = self.prompts_dir / platform
            if platform_dir.exists():
                prompt_file = platform_dir / "post_prompts.py"
                if prompt_file.exists():
                    try:
                        spec = importlib.util.spec_from_file_location(
                            f"{platform}_prompts", 
                            prompt_file
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        self._loaded_prompts[platform] = {
                            "posts": getattr(module, f"{platform.upper()}_POST_PROMPTS", {}),
                            "stories": getattr(module, f"{platform.upper()}_STORY_PROMPTS", {})
                        }
                        
                        logger.info(f"Loaded prompts for {platform}")
                    except Exception as e:
                        logger.error(f"Failed to load prompts for {platform}: {str(e)}")
                        self._loaded_prompts[platform] = {"posts": {}, "stories": {}}
                else:
                    logger.warning(f"Prompt file not found for {platform}")
                    self._loaded_prompts[platform] = {"posts": {}, "stories": {}}
            else:
                logger.warning(f"Platform directory not found: {platform}")
                self._loaded_prompts[platform] = {"posts": {}, "stories": {}}
    
    def get_prompt(
        self,
        platform: str,
        content_type: str,
        text_length: str,
        input_text: Optional[str] = None,
        newspaper: Optional[str] = None
    ) -> str:
        """
        Get a formatted prompt for the specified parameters.
        
        Args:
            platform: Target platform (instagram, facebook, linkedin)
            content_type: Content type (post, story)
            text_length: Text length (short, medium, long)
            input_text: Optional input text to base content on
            newspaper: Regional newspaper brand
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If platform, content_type, or text_length is not supported
        """
        # Validate platform
        if platform not in self._loaded_prompts:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Normalize content type (handle both singular and plural)
        content_type_normalized = content_type.lower()
        if content_type_normalized == "post":
            content_type_normalized = "posts"
        elif content_type_normalized == "story":
            content_type_normalized = "stories"
        
        # Validate content type
        if content_type_normalized not in self._loaded_prompts[platform]:
            available_types = list(self._loaded_prompts[platform].keys())
            logger.error(f"Content type mismatch for {platform}: requested '{content_type}' (normalized: '{content_type_normalized}'), available: {available_types}")
            raise ValueError(f"Unsupported content type for {platform}: {content_type} (available: {', '.join(available_types)})")
        
        # Get the prompt template
        prompt_templates = self._loaded_prompts[platform][content_type_normalized]
        
        if text_length not in prompt_templates:
            # Fallback to medium if length not available
            if "medium" in prompt_templates:
                text_length = "medium"
                logger.warning(f"Text length '{text_length}' not available for {platform} {content_type}, using 'medium'")
            else:
                # Use the first available length
                text_length = list(prompt_templates.keys())[0]
                logger.warning(f"Using '{text_length}' for {platform} {content_type}")
        
        prompt_template = prompt_templates[text_length]
        
        # Prepare input text context
        input_text_context = ""
        if input_text:
            input_text_context = f"\nBase your content on this input: {input_text}\n"
        
        # Format the prompt
        formatted_prompt = prompt_template.format(
            newspaper=newspaper or 'Kaleva Media',
            input_text_context=input_text_context
        )
        
        logger.info(f"Generated prompt for {platform} {content_type} {text_length}")
        return formatted_prompt
    
    def get_available_lengths(self, platform: str, content_type: str) -> list:
        """
        Get available text lengths for a platform and content type.
        
        Args:
            platform: Target platform
            content_type: Content type
            
        Returns:
            List of available text lengths
        """
        if platform not in self._loaded_prompts:
            return []
        
        if content_type not in self._loaded_prompts[platform]:
            return []
        
        return list(self._loaded_prompts[platform][content_type].keys())
    
    def get_supported_platforms(self) -> list:
        """Get list of supported platforms."""
        return list(self._loaded_prompts.keys())
    
    def get_supported_content_types(self, platform: str) -> list:
        """Get list of supported content types for a platform."""
        if platform not in self._loaded_prompts:
            return []
        
        return list(self._loaded_prompts[platform].keys())
    
    def reload_prompts(self):
        """Reload all prompts from files."""
        logger.info("Reloading all prompts")
        self._loaded_prompts = {}
        self._load_all_prompts()


# Create singleton instance
prompt_manager = PromptManager()


