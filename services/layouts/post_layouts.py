"""
Post layout handlers for Portrait and Square layouts.
Handles 4 different visual versions for each layout.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Dict
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs


class PostLayoutHandler:
    """Handler for Portrait and Square post layouts with 4 visual versions."""
    
    def __init__(self, graphic_composer):
        """Initialize with reference to graphic composer for shared methods."""
        self.graphic_composer = graphic_composer
    
    def create_portrait_post(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                           content_type: str, campaign_type: str, colors: Dict, 
                           width: int, height: int, version: int, banner_text: str = None) -> Image.Image:
        """Create Portrait post with specified version."""
        if version == 1:
            return self._create_portrait_post_version_1(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        elif version == 2:
            return self._create_portrait_post_version_2(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        elif version == 3:
            return self._create_portrait_post_version_3(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
        else:  # version == 4
            return self._create_portrait_post_version_4(canvas, heading_text, newspaper, 
                                                      content_type, campaign_type, colors, width, height, banner_text)
    
    def create_square_post(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                         content_type: str, campaign_type: str, colors: Dict, 
                         width: int, height: int, version: int) -> Image.Image:
        """Create Square post with specified version (same as portrait)."""
        # Square posts use the same layout as portrait posts
        return self.create_portrait_post(canvas, heading_text, newspaper, content_type, 
                                       campaign_type, colors, width, height, version)
    
    def _create_portrait_post_version_1(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                     content_type: str, campaign_type: str, colors: Dict, 
                                     width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 1: Semi-transparent overlay transitioning to solid background (Lapin Kansa style)."""
        # Add campaign banner only if specified
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner(canvas, colors, content_type, width, height, banner_text, version=1)
        
        # Add semi-transparent overlay transitioning to solid background
        canvas = self.graphic_composer._add_semi_transparent_overlay(canvas, colors, width, height)
        
        # Add newspaper logo at bottom center
        canvas = self.graphic_composer._add_newspaper_logo_bottom(canvas, newspaper, colors, width, height)
        
        # Add main headline (overlapping photo and background)
        canvas = self.graphic_composer._add_headline(canvas, heading_text, width, height, newspaper, content_type)
        
        return canvas
    
    def _create_portrait_post_version_2(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                     content_type: str, campaign_type: str, colors: Dict, 
                                     width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 2: Clean layout with top headline and bottom-left logo (KALEVA style)."""
        # Add campaign banner only if specified
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner(canvas, colors, content_type, width, height, banner_text, version=2)
        
        # Add headline at top
        canvas = self.graphic_composer._add_headline_top(canvas, heading_text, width, height, newspaper, content_type)
        
        # Add newspaper logo at bottom left
        canvas = self.graphic_composer._add_newspaper_logo_bottom_left(canvas, newspaper, colors, width, height)
        
        return canvas
    
    def _create_portrait_post_version_3(self, canvas: Image.Image, heading_text: str, newspaper: str, 
                                     content_type: str, campaign_type: str, colors: Dict, 
                                     width: int, height: int, banner_text: str = None) -> Image.Image:
        """Version 3: Top-left logo with bottom center headline."""
        # Add newspaper logo at top left
        canvas = self.graphic_composer._add_newspaper_logo_top_left(canvas, newspaper, colors, width, height)
        
        # Add campaign banner above headline if specified
        if campaign_type != "logo_only":
            canvas = self.graphic_composer._add_campaign_banner_bottom_center(canvas, colors, content_type, width, height, banner_text)
        
        # Add headline at bottom center
        canvas = self.graphic_composer._add_headline_bottom_center(canvas, heading_text, width, height, newspaper, content_type)
        
        return canvas
    
    def _create_portrait_post_version_4(self, canvas: Image.Image, heading_text: str, newspaper: str, 
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
