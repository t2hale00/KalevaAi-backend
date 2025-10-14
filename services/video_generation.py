"""
Video generation service for creating motion-style graphics.
Uses MoviePy for video creation with simple transitions.
"""
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
from typing import Optional, List
from pathlib import Path
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
import cv2

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
        
        # Create video using OpenCV instead of MoviePy to avoid ImageMagick dependency
        logger.info("Creating video frames with text overlay using OpenCV")
        
        # Import graphic composer to create a branded frame
        from services.graphic_composer import graphic_composer
        
        # Create a temporary branded image with text
        temp_image_path = str(Path(output_path).parent / f"temp_{Path(output_path).stem}.png")
        
        graphic_composer.create_branded_social_graphic(
            input_image_path=input_image_path,
            heading_text=heading_text,
            description_text="",  # No description for video
            newspaper=newspaper,
            platform=platform,
            content_type=content_type,
            layout=layout,
            output_path=temp_image_path,
            campaign_type="none"
        )
        
        # Create video with animations using OpenCV
        base_img = cv2.imread(temp_image_path)
        height, width, layers = base_img.shape
        
        # Define the codec and create VideoWriter object
        # Use H264 codec for better compatibility
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        video = cv2.VideoWriter(output_path, fourcc, 30, (width, height))
        
        # Check if video writer opened successfully
        if not video.isOpened():
            logger.warning("H264 codec failed, trying mp4v")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, 30, (width, height))
        
        # Create animated frames
        fps = 30
        total_frames = duration * fps
        
        logger.info(f"Generating {total_frames} animated frames at {fps} fps")
        
        for frame_num in range(total_frames):
            # Calculate progress (0 to 1)
            progress = frame_num / total_frames
            
            # Create animated frame with effects
            animated_frame = self._apply_animation_effects(
                base_img.copy(),
                progress,
                width,
                height
            )
            
            video.write(animated_frame)
            
            # Log progress every 30 frames (every second)
            if frame_num % 30 == 0:
                logger.debug(f"Generated frame {frame_num}/{total_frames} (progress: {progress:.1%})")
        
        # Release the video writer
        video.release()
        
        # Clean up temporary image
        try:
            Path(temp_image_path).unlink()
        except:
            pass
        
        logger.info(f"Motion graphic saved to {output_path}")
        
        return output_path
    
    def _apply_animation_effects(self, frame, progress, width, height):
        """
        Apply PowerPoint-style animation effects to the frame.
        
        Effects:
        - Zoom in effect: Image zooms from 100% to 120%
        - Fade in effect: Fades in from black
        - Pan effect: Slight horizontal movement
        """
        # Effect 1: Strong Zoom effect (Ken Burns style)
        # More aggressive zoom for visibility
        zoom_factor = 1.0 + (0.25 * progress)  # Zoom from 100% to 125%
        
        # Calculate new dimensions
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        # Resize frame with smooth interpolation
        zoomed = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Effect 2: Pan effect (slight horizontal movement)
        # Pan from left to center
        pan_offset = int((new_width - width) * (0.5 - progress * 0.3))
        start_x = max(0, min(pan_offset, new_width - width))
        start_y = (new_height - height) // 2
        
        # Ensure we don't go out of bounds
        if start_x + width > new_width:
            start_x = new_width - width
        if start_y + height > new_height:
            start_y = new_height - height
            
        cropped = zoomed[start_y:start_y + height, start_x:start_x + width]
        
        # Effect 3: Fade in effect (first 1.5 seconds)
        if progress < 0.3:  # First 30% of video
            fade_progress = progress / 0.3
            # Smooth fade curve
            fade_progress = fade_progress ** 0.5  # Ease out
            # Apply fade by blending with black
            black = np.zeros_like(cropped)
            cropped = cv2.addWeighted(black, 1 - fade_progress, cropped, fade_progress, 0)
        
        # Effect 4: Brightness enhancement (subtle throughout)
        if progress > 0.3:  # After fade in
            brightness_boost = 1.0 + (0.1 * (progress - 0.3))  # Gradually brighten
            cropped = cv2.convertScaleAbs(cropped, alpha=min(brightness_boost, 1.15), beta=5)
        
        return cropped


# Create singleton instance
video_generation_service = VideoGenerationService()


