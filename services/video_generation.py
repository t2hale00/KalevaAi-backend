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
        duration: int = 3,
        effect_type: str = "zoom_pan",
        version: int = 1
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
            effect_type: Type of animation effect ("zoom_pan" or "fade_rotate")
            version: Visual version/style (1 or 2) for different layouts
            
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
        logger.info("Creating video frames with separate photo and text effects")
        
        # Import graphic composer to create layered frames
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
            campaign_type="logo_only",
            version=version  # Use different visual style
        )
        
        # Load the complete branded image
        base_img = cv2.imread(temp_image_path)
        height, width, layers = base_img.shape
        
        # Create a photo-only layer (without text) for separate animation
        temp_photo_path = str(Path(output_path).parent / f"temp_photo_{Path(output_path).stem}.png")
        graphic_composer.create_branded_social_graphic(
            input_image_path=input_image_path,
            heading_text="",  # No text for photo layer
            description_text="",
            newspaper=newspaper,
            platform=platform,
            content_type=content_type,
            layout=layout,
            output_path=temp_photo_path,
            campaign_type="logo_only",
            version=version  # Use same visual style for photo layer
        )
        photo_img = cv2.imread(temp_photo_path)
        
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
            
            # Apply separate effects to photo and text layers
            animated_frame = self._apply_layered_animation_effects(
                photo_img.copy(),
                base_img.copy(),
                progress,
                width,
                height,
                effect_type
            )
            
            video.write(animated_frame)
            
            # Log progress every 30 frames (every second)
            if frame_num % 30 == 0:
                logger.debug(f"Generated frame {frame_num}/{total_frames} (progress: {progress:.1%})")
        
        # Release the video writer
        video.release()
        
        # Clean up temporary images
        try:
            Path(temp_image_path).unlink()
            Path(temp_photo_path).unlink()
        except:
            pass
        
        logger.info(f"Motion graphic saved to {output_path}")
        
        return output_path
    
    def _apply_layered_animation_effects(self, photo_frame, text_frame, progress, width, height, effect_type="zoom_pan"):
        """
        Apply separate effects to photo and text layers for PowerPoint-style animations.
        
        Args:
            photo_frame: Photo layer without text
            text_frame: Complete image with text
            progress: Animation progress (0 to 1)
            width: Target width
            height: Target height
            effect_type: Type of effect to apply ("zoom_pan" or "fade_rotate")
        """
        if effect_type == "zoom_pan":
            return self._apply_zoom_pan_layered(photo_frame, text_frame, progress, width, height)
        elif effect_type == "fade_rotate":
            return self._apply_fade_rotate_layered(photo_frame, text_frame, progress, width, height)
        else:
            return text_frame
    
    def _apply_animation_effects(self, frame, progress, width, height, effect_type="zoom_pan"):
        """
        Apply PowerPoint-style animation effects to the frame.
        
        Effects:
        - zoom_pan: Zoom in effect with horizontal pan movement
        - fade_rotate: Fade in with subtle rotation
        
        Args:
            frame: Input frame as numpy array
            progress: Animation progress (0 to 1)
            width: Target width
            height: Target height
            effect_type: Type of effect to apply ("zoom_pan" or "fade_rotate")
        """
        if effect_type == "zoom_pan":
            return self._apply_zoom_pan_effects(frame, progress, width, height)
        elif effect_type == "fade_rotate":
            return self._apply_fade_rotate_effects(frame, progress, width, height)
        else:
            return frame
    
    def _apply_zoom_pan_layered(self, photo_frame, text_frame, progress, width, height):
        """
        PowerPoint transition: Photo uses "Fade" and text uses "Wipe Up" effect.
        Clean, professional look matching PowerPoint's elegant transitions.
        """
        # Photo effect: Fade In (PowerPoint Fade transition)
        # Fast fade from black
        ease_progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
        photo_fade_progress = min(progress / 0.3, 1.0)  # Complete in first 30%
        photo_alpha = photo_fade_progress ** 0.8  # Smooth ease-out
        
        # Apply fade to photo
        black = np.zeros_like(photo_frame)
        photo_faded = cv2.addWeighted(black, 1 - photo_alpha, photo_frame, photo_alpha, 0)
        
        # Extract text layer first
        text_layer = cv2.absdiff(text_frame, photo_frame)
        text_mask_gray = cv2.cvtColor(text_layer, cv2.COLOR_BGR2GRAY)
        _, text_mask = cv2.threshold(text_mask_gray, 10, 255, cv2.THRESH_BINARY)
        
        # Text effect: Wipe Up (PowerPoint Wipe Up transition)
        # Text wipes in from bottom to top
        text_progress = max(0, (progress - 0.3) / 0.7)  # Start after photo fade, end at 100%
        text_ease = text_progress * text_progress * (3.0 - 2.0 * text_progress)
        
        # Create wipe mask from bottom to top for text only
        wipe_height = int(height * text_ease)
        text_wipe_mask = np.zeros((height, width), dtype=np.uint8)
        text_wipe_mask[height - wipe_height:height, :] = 255
        
        # Apply wipe to text mask
        text_animated_mask = cv2.bitwise_and(text_mask, text_wipe_mask)
        text_mask_normalized = text_animated_mask.astype(np.float32) / 255.0
        
        # Blend animated text over faded photo
        for c in range(3):
            photo_faded[:, :, c] = photo_faded[:, :, c] * (1 - text_mask_normalized) + text_frame[:, :, c] * text_mask_normalized
        
        return photo_faded
    
    def _apply_zoom_pan_effects(self, frame, progress, width, height):
        """
        Apply zoom and pan effects (version 1) - PowerPoint style with faster animation.
        
        Effects:
        - Fast zoom and pan to center position
        - Quick fade in effect
        - Smooth brightness enhancement
        """
        # Effect 1: Fast Zoom effect (Ken Burns style) - reaches target by 50% of video
        # Use ease-in-out curve for PowerPoint-like animation
        ease_progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
        zoom_factor = 1.0 + (0.20 * ease_progress)  # Zoom from 100% to 120%
        
        # Calculate new dimensions
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        # Resize frame with smooth interpolation
        zoomed = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Effect 2: Fast pan to center - smooth ease-in-out
        # Pan from offset position to center (0.5 = center)
        pan_progress = ease_progress
        center_pos = 0.5  # Always center at the end
        pan_offset = int((new_width - width) * center_pos * (1 - pan_progress))
        start_x = max(0, min(pan_offset, new_width - width))
        start_y = (new_height - height) // 2
        
        # Ensure we don't go out of bounds
        if start_x + width > new_width:
            start_x = new_width - width
        if start_y + height > new_height:
            start_y = new_height - height
            
        cropped = zoomed[start_y:start_y + height, start_x:start_x + width]
        
        # Effect 3: Fast fade in effect (first 15% of video) - PowerPoint style
        if progress < 0.15:
            fade_progress = progress / 0.15
            fade_progress = fade_progress ** 0.5  # Ease out
            black = np.zeros_like(cropped)
            cropped = cv2.addWeighted(black, 1 - fade_progress, cropped, fade_progress, 0)
        
        # Effect 4: Brightness enhancement
        if progress > 0.15:
            brightness_boost = 1.0 + (0.1 * (progress - 0.15))
            cropped = cv2.convertScaleAbs(cropped, alpha=min(brightness_boost, 1.1), beta=3)
        
        return cropped
    
    def _apply_fade_rotate_layered(self, photo_frame, text_frame, progress, width, height):
        """
        PowerPoint transition: Photo uses "Wipe Right" and text uses "Fly In from Bottom" effect.
        Dynamic presentation style with movement.
        """
        # Photo effect: Wipe Right (PowerPoint Wipe Right transition)
        # Image wipes in from left to right
        photo_progress = min(progress / 0.4, 1.0)  # Complete in first 40%
        photo_ease = photo_progress * photo_progress * (3.0 - 2.0 * photo_progress)
        
        # Create wipe mask from left to right
        wipe_width = int(width * photo_ease)
        photo_wipe = np.zeros_like(photo_frame)
        photo_wipe[:, :wipe_width] = photo_frame[:, :wipe_width]
        
        # Extract text layer first
        text_layer = cv2.absdiff(text_frame, photo_frame)
        text_mask_gray = cv2.cvtColor(text_layer, cv2.COLOR_BGR2GRAY)
        _, text_mask = cv2.threshold(text_mask_gray, 10, 255, cv2.THRESH_BINARY)
        
        # Text effect: Fly In from Bottom (PowerPoint Fly In transition)
        # Text flies in from the bottom
        text_progress = max(0, (progress - 0.4) / 0.6)  # Start after photo, end at 100%
        text_ease = text_progress * text_progress * (3.0 - 2.0 * text_progress)
        
        # Calculate fly distance
        fly_distance = int(height * 0.2 * (1 - text_ease))  # Fly 20% of height
        
        # Create text with fly in effect from bottom
        text_fly = np.zeros_like(text_frame)
        if fly_distance > 0:
            text_fly[:height - fly_distance, :] = text_frame[fly_distance:, :]
        else:
            text_fly = text_frame
        
        # Apply fade and fly effect to text
        text_alpha = text_ease ** 0.8
        
        # Create fly mask for text
        text_fly_mask = np.zeros((height, width), dtype=np.uint8)
        text_fly_mask[:height - fly_distance, :] = 255
        
        # Apply fly and fade to text mask
        text_animated_mask = cv2.bitwise_and(text_mask, text_fly_mask)
        text_mask_normalized = text_animated_mask.astype(np.float32) / 255.0 * text_alpha
        
        # Blend animated text over wiped photo
        for c in range(3):
            photo_wipe[:, :, c] = photo_wipe[:, :, c] * (1 - text_mask_normalized) + text_fly[:, :, c] * text_mask_normalized
        
        return photo_wipe
    
    def _apply_fade_rotate_effects(self, frame, progress, width, height):
        """
        Apply fade and rotate effects (version 2) - PowerPoint style with faster animation.
        
        Effects:
        - Fast fade in
        - Quick rotation that settles at center
        - Smooth pulse effect
        - Contrast enhancement
        """
        # Effect 1: Very fast fade in effect (first 10% of video)
        if progress < 0.1:
            fade_progress = progress / 0.1
            fade_progress = fade_progress ** 0.7  # Smooth fade
            black = np.zeros_like(frame)
            frame = cv2.addWeighted(black, 1 - fade_progress, frame, fade_progress, 0)
        
        # Effect 2: Fast rotation that reaches final position early
        # Use ease-out for smooth deceleration
        ease_progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
        angle = ease_progress * 5  # Rotate up to 5 degrees with ease-out
        rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1.0)
        rotated = cv2.warpAffine(frame, rotation_matrix, (width, height), 
                                flags=cv2.INTER_LINEAR, 
                                borderMode=cv2.BORDER_REPLICATE)
        
        # Effect 3: Smooth pulse effect (gentle zoom pulse)
        pulse_progress = abs(np.sin(progress * np.pi * 3)) * 0.03  # Gentler pulse
        scale_factor = 1.0 + pulse_progress
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        scaled = cv2.resize(rotated, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Crop center - always keep content centered
        start_x = max(0, (new_width - width) // 2)
        start_y = max(0, (new_height - height) // 2)
        cropped = scaled[start_y:start_y + height, start_x:start_x + width]
        
        # Effect 4: Smooth contrast enhancement
        if progress > 0.1:
            contrast_boost = 1.0 + (0.1 * (progress - 0.1))
            cropped = cv2.convertScaleAbs(cropped, alpha=min(contrast_boost, 1.1), beta=5)
        
        return cropped


# Create singleton instance
video_generation_service = VideoGenerationService()


