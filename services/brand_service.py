"""
Brand service for managing brand assets and specifications.
"""
from pathlib import Path
from typing import Optional
from loguru import logger

from models.brand_config import get_brand_specs, get_platform_specs, BRAND_SPECIFICATIONS


class BrandService:
    """Service for managing brand assets and specifications."""
    
    def __init__(self):
        """Initialize brand service."""
        self.assets_dir = Path("assets")
        self.logos_dir = self.assets_dir / "logos"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure brand asset directories exist."""
        self.assets_dir.mkdir(exist_ok=True)
        self.logos_dir.mkdir(exist_ok=True)
    
    def get_brand_specifications(self, newspaper: str) -> dict:
        """
        Get complete brand specifications for a newspaper.
        
        Args:
            newspaper: Newspaper name
            
        Returns:
            Dictionary with brand specifications
        """
        brand_specs = get_brand_specs(newspaper)
        
        if not brand_specs:
            raise ValueError(f"Unknown newspaper: {newspaper}")
        
        return {
            "name": brand_specs.name,
            "logo_path": brand_specs.logo_path,
            "color_palette": brand_specs.color_palette,
            "font_family": brand_specs.font_family,
            "font_color": brand_specs.font_color,
            "font_size_story": brand_specs.font_size_story,
            "font_size_post": brand_specs.font_size_post,
            "title_location_post": brand_specs.title_location_post,
            "title_location_story": brand_specs.title_location_story
        }
    
    def get_platform_requirements(
        self,
        platform: str,
        content_type: str,
        layout: str
    ) -> dict:
        """
        Get platform technical requirements.
        
        Args:
            platform: Platform name
            content_type: Content type (post/story)
            layout: Layout type
            
        Returns:
            Dictionary with platform specifications
        """
        specs = get_platform_specs(platform, content_type, layout)
        
        if not specs:
            raise ValueError(f"Invalid platform configuration: {platform}/{content_type}/{layout}")
        
        return specs
    
    def validate_brand_assets(self, newspaper: str) -> bool:
        """
        Check if brand assets (logos, fonts) are available.
        
        Args:
            newspaper: Newspaper name
            
        Returns:
            True if assets are available
        """
        brand_specs = get_brand_specs(newspaper)
        
        if not brand_specs:
            return False
        
        # Check if logo exists
        logo_path = Path(brand_specs.logo_path)
        logo_exists = logo_path.exists()
        
        if not logo_exists:
            logger.warning(f"Logo not found for {newspaper} at {logo_path}")
        
        return logo_exists
    
    def list_available_newspapers(self) -> list:
        """Get list of all available newspapers."""
        return list(BRAND_SPECIFICATIONS.keys())


# Create singleton instance
brand_service = BrandService()


