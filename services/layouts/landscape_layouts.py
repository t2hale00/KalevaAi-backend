"""
Landscape layout handlers for Posts and Stories.
Handles split-screen design with photo on left and solid color panel on right.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Dict
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs


class LandscapeLayoutHandler:
    """Handler for Landscape layouts with split-screen design."""
    
    def __init__(self, graphic_composer):
        """Initialize with reference to graphic composer for shared methods."""
        self.graphic_composer = graphic_composer
    
    def create_landscape_post(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                            content_type: str, campaign_type: str, colors: Dict, 
                            width: int, height: int, version: int = 2, banner_text: str = None) -> Image.Image:
        """Create Landscape post with split-screen design (v1: left panel, v2: right panel)."""
        # Add campaign banner only if specified (upper-left of photo section)
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_landscape(canvas, colors, content_type, width, height, banner_text, version)
        
        # Create split-screen layout
        canvas = self.graphic_composer._create_split_screen_layout(canvas, colors, width, height, version)
        
        # Add headline on solid color panel
        canvas = self.graphic_composer._add_headline_landscape(canvas, heading_text, width, height, newspaper, content_type, version)
        
        # Add newspaper logo on solid color panel
        canvas = self.graphic_composer._add_newspaper_logo_landscape(canvas, newspaper, colors, width, height, version)
        
        return canvas
    
    def create_landscape_story(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                             content_type: str, campaign_type: str, colors: Dict, 
                             width: int, height: int, version: int = 2, banner_text: str = None) -> Image.Image:
        """Create Landscape story with split-screen design (same as post)."""
        # Landscape stories use the same layout as landscape posts
        return self.create_landscape_post(canvas, heading_text, newspaper, content_type, 
                                        campaign_type, colors, width, height, version, banner_text)
