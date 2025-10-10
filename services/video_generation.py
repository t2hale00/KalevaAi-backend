"""
Video generation service for creating motion-style graphics.
Uses MoviePy for video creation with simple transitions.
"""
from moviepy.editor import ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
import numpy as np
from typing import Optional, List
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs, get_platform_specs


class VideoGenerationService:
    """Service for creating motion-style animated graphics."""
    
    def create_motion_graphic(
        self,
        input_image_path: str,
        heading_text: str,
        newspaper: str,
        platform: str,
        content_type: str,
        layout: str,
        output_path: str,
        duration: int = 5
    ) -> str:
        """
        Create a motion-style graphic with animations.
        
        Args:
            input_image_path: Path to input image
            heading_text: Text to overlay on image
            newspaper: Regional newspaper brand
            platform: Target platform
            content_type: Content type (post/story)
            layout: Layout type
            output_path: Path to save output video
            duration: Video duration in seconds
            
        Returns:
            Path to created video
        """
        logger.info(f"Creating motion graphic for {newspaper} - {platform} {content_type}")
        
        # Get brand and platform specifications
        brand_specs = get_brand_specs(newspaper)
        platform_specs = get_platform_specs(platform, content_type, layout)
        
        if not brand_specs or not platform_specs:
            raise ValueError(f"Invalid specifications for {newspaper} or {platform}")
        
        target_width = platform_specs["width"]
        target_height = platform_specs["height"]
        
        # Create base image clip with zoom effect
        image_clip = (ImageClip(input_image_path)
                     .resize((target_width, target_height))
                     .set_duration(duration)
                     .fx(self._zoom_effect))
        
        # Create text overlay with fade-in effect
        text_clip = self._create_text_clip(
            heading_text,
            brand_specs,
            content_type,
            target_width,
            target_height,
            duration
        )
        
        # Composite video with image and text
        final_clip = CompositeVideoClip([image_clip, text_clip])
        
        # Write video file
        final_clip.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio=False,
            preset='medium'
        )
        
        logger.info(f"Motion graphic saved to {output_path}")
        
        return output_path
    
    def _zoom_effect(self, get_frame, t):
        """Apply subtle zoom effect to video."""
        frame = get_frame(t)
        # Subtle zoom from 100% to 110%
        zoom_factor = 1 + 0.1 * (t / 5)  # Assuming 5 second duration
        h, w = frame.shape[:2]
        
        # Calculate crop for zoom
        new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
        y1 = (h - new_h) // 2
        x1 = (w - new_w) // 2
        
        cropped = frame[y1:y1+new_h, x1:x1+new_w]
        zoomed = np.array(Image.fromarray(cropped).resize((w, h)))
        
        return zoomed
    
    def _create_text_clip(
        self,
        text: str,
        brand_specs,
        content_type: str,
        width: int,
        height: int,
        duration: int
    ) -> TextClip:
        """Create text clip with animations."""
        font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        
        # Determine position
        title_location = (
            brand_specs.title_location_story if content_type == "story"
            else brand_specs.title_location_post
        )
        
        position = self._get_text_position(title_location)
        
        # Create text clip (simplified - full implementation would use custom fonts)
        text_clip = (TextClip(
            text,
            fontsize=font_size,
            color=brand_specs.font_color,
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(width - 80, None)  # Width with margin
        )
        .set_duration(duration)
        .set_position(position)
        .crossfadein(0.5))  # Fade in effect
        
        return text_clip
    
    def _get_text_position(self, location: str) -> tuple:
        """Get text position for video overlay."""
        positions = {
            "top-left": ("left", "top"),
            "top-right": ("right", "top"),
            "top-center": ("center", "top"),
            "center": ("center", "center"),
            "bottom-left": ("left", "bottom"),
            "bottom-right": ("right", "bottom"),
        }
        return positions.get(location, ("left", "top"))


# Create singleton instance
video_generation_service = VideoGenerationService()


