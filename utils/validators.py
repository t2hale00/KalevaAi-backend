"""
Input validation utilities.
"""
from typing import Optional
from loguru import logger

from models.brand_config import get_platform_specs, BRAND_SPECIFICATIONS


class ContentValidator:
    """Validate content generation requests."""
    
    @staticmethod
    def validate_platform_layout_combination(
        platform: str,
        content_type: str,
        layout: str
    ) -> bool:
        """
        Validate that platform, content type, and layout combination is valid.
        
        Args:
            platform: Platform name
            content_type: Content type
            layout: Layout type
            
        Returns:
            True if valid combination
        """
        specs = get_platform_specs(platform, content_type, layout)
        
        if not specs:
            logger.warning(f"Invalid combination: {platform}/{content_type}/{layout}")
            return False
        
        return True
    
    @staticmethod
    def validate_newspaper(newspaper: str) -> bool:
        """
        Validate that newspaper exists in brand specifications.
        
        Args:
            newspaper: Newspaper name
            
        Returns:
            True if valid newspaper
        """
        valid = newspaper in BRAND_SPECIFICATIONS
        
        if not valid:
            logger.warning(f"Unknown newspaper: {newspaper}")
        
        return valid
    
    @staticmethod
    def validate_text_length(text: str, max_length: int) -> bool:
        """
        Validate text length.
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Returns:
            True if within limit
        """
        valid = len(text) <= max_length
        
        if not valid:
            logger.warning(f"Text too long: {len(text)} > {max_length}")
        
        return valid
    
    @staticmethod
    def validate_content_request(
        platform: str,
        content_type: str,
        layout: str,
        newspaper: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate complete content generation request.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate newspaper
        if not ContentValidator.validate_newspaper(newspaper):
            return False, f"Invalid newspaper: {newspaper}"
        
        # Validate platform/content/layout combination
        if not ContentValidator.validate_platform_layout_combination(platform, content_type, layout):
            return False, f"Invalid combination: {platform}/{content_type}/{layout}"
        
        return True, None


# Create singleton instance
content_validator = ContentValidator()




