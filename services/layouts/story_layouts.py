"""
Story layout handlers for Portrait and Square layouts.
Handles 4 different visual versions for stories with campaign banner in upper-right.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Dict
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs


class StoryLayoutHandler:
    """Handler for Portrait and Square story layouts with 4 visual versions."""
    
    def __init__(self, graphic_composer):
        """Initialize with reference to graphic composer for shared methods."""
        self.graphic_composer = graphic_composer
    
    def create_portrait_story(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                            content_type: str, campaign_type: str, colors: Dict, 
                            width: int, height: int, version: int = 1, banner_text: str = None) -> Image.Image:
        """Create Portrait story with specified version."""
        if version == 1:
            return self._create_portrait_story_version_1(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        elif version == 2:
            return self._create_portrait_story_version_2(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        elif version == 3:
            return self._create_portrait_story_version_3(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        else:  # version == 4
            return self._create_portrait_story_version_4(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
    
    def create_square_story(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                          content_type: str, campaign_type: str, colors: Dict, 
                          width: int, height: int, version: int = 1, banner_text: str = None) -> Image.Image:
        """Create Square story with specified version (same as portrait)."""
        # Square stories use the same layout as portrait stories
        return self.create_portrait_story(canvas, heading_text, newspaper, content_type, 
                                        campaign_type, colors, width, height, version, banner_text)
    
    def _create_portrait_story_version_1(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                       content_type: str, campaign_type: str, colors: Dict, 
                                       width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 1: Solid background with overlapping text (Lapin Kansa story style)."""
        # Add campaign banner only if specified (upper-right for stories)
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_story(canvas, colors, content_type, width, height, banner_text)
        
        # Add newspaper color background overlay at bottom
        canvas = self.graphic_composer._add_newspaper_background_overlay(canvas, colors, width, height)
        
        # Add newspaper logo at bottom center
        canvas = self.graphic_composer._add_newspaper_logo_bottom_story(canvas, newspaper, colors, width, height)
        
        # Add main headline (overlapping photo and background)
        canvas = self.graphic_composer._add_headline(canvas, heading_text, width, height, newspaper, content_type)
        
        return canvas
    
    def _create_portrait_story_version_2(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                       content_type: str, campaign_type: str, colors: Dict, 
                                       width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 2: Clean layout with centered headline and bottom logo (KALEVA story style)."""
        # Add campaign banner only if specified (upper-right for stories)
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_story(canvas, colors, content_type, width, height, banner_text)
        
        # Add headline centered on image
        canvas = self.graphic_composer._add_headline_centered(canvas, heading_text, width, height, newspaper, content_type)
        
        # Add newspaper logo at bottom center
        canvas = self.graphic_composer._add_newspaper_logo_bottom_story(canvas, newspaper, colors, width, height)
        
        return canvas
    
    def _create_portrait_story_version_3(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                       content_type: str, campaign_type: str, colors: Dict, 
                                       width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 3: Top-left logo with bottom center headline."""
        # Add newspaper logo at top left
        canvas = self.graphic_composer._add_newspaper_logo_top_left(canvas, newspaper, colors, width, height)
        
        # Add headline at bottom center
        canvas = self.graphic_composer._add_headline_bottom_center(canvas, heading_text, width, height, newspaper, content_type)
        
        # Add campaign banner below headline if specified
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_bottom_center(canvas, colors, content_type, width, height, banner_text)
        
        return canvas
    
    def _create_portrait_story_version_4(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                       content_type: str, campaign_type: str, colors: Dict, 
                                       width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 4: Headline inside solid panel and logo at top center."""
        # Add background overlay first to create the solid panel
        canvas = self.graphic_composer._add_newspaper_background_overlay(canvas, colors, width, height)
        
        # Add logo at top center (now brighter and bigger)
        canvas = self.graphic_composer._add_newspaper_logo_top_center(canvas, newspaper, colors, width, height)
        
        # Add campaign banner inside the solid panel, above the heading, only if specified
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_in_panel(canvas, colors, content_type, width, height, banner_text)
        
        # Add headline inside the solid panel
        canvas = self.graphic_composer._add_headline_in_panel(canvas, heading_text, width, height, newspaper, content_type)
        
        return canvas
