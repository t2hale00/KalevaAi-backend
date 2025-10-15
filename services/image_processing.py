"""
Image processing service for creating static branded graphics.
Uses Pillow and OpenCV for image manipulation.
"""
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from typing import Tuple
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs, get_platform_specs


class ImageProcessingService:
    """Service for creating static branded graphics."""
    
    def _load_font(self, font_size: int, font_family: str = "Axiforma") -> ImageFont.FreeTypeFont:
        """Load font with proper fallback chain."""
        # Try to load Axiforma from various possible locations
        possible_paths = [
            # Local assets directory
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family}.ttf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family}.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family.lower()}.ttf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family.lower()}.otf",
            # System fonts (Windows)
            Path("C:/Windows/Fonts") / f"{font_family}.ttf",
            Path("C:/Windows/Fonts") / f"{font_family}.otf",
            Path("C:/Windows/Fonts") / f"{font_family.lower()}.ttf",
            Path("C:/Windows/Fonts") / f"{font_family.lower()}.otf",
            # System fonts (macOS)
            Path("/System/Library/Fonts") / f"{font_family}.ttf",
            Path("/System/Library/Fonts") / f"{font_family}.otf",
            Path("/Library/Fonts") / f"{font_family}.ttf",
            Path("/Library/Fonts") / f"{font_family}.otf",
            # System fonts (Linux)
            Path("/usr/share/fonts/truetype") / f"{font_family.lower()}.ttf",
            Path("/usr/share/fonts/opentype") / f"{font_family.lower()}.otf",
        ]
        
        for font_path in possible_paths:
            if font_path.exists():
                try:
                    font = ImageFont.truetype(str(font_path), font_size)
                    logger.info(f"Loaded font: {font_path}")
                    return font
                except (OSError, IOError) as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")
                    continue
        
        # Fallback to system fonts
        try:
            # Try Arial (common on Windows)
            font = ImageFont.truetype("arial.ttf", font_size)
            logger.warning("Using Arial fallback font")
            return font
        except (OSError, IOError):
            try:
                # Try Helvetica (common on macOS)
                font = ImageFont.truetype("Helvetica.ttc", font_size)
                logger.warning("Using Helvetica fallback font")
                return font
            except (OSError, IOError):
                # Final fallback to default
                logger.warning("Using PIL default font")
                return ImageFont.load_default()
    
    def create_branded_graphic(
        self,
        input_image_path: str,
        heading_text: str,
        newspaper: str,
        platform: str,
        content_type: str,
        layout: str,
        output_path: str
    ) -> str:
        """
        Create a branded graphic with text overlay and branding.
        
        Args:
            input_image_path: Path to input image
            heading_text: Text to overlay on image
            newspaper: Regional newspaper brand
            platform: Target platform
            content_type: Content type (post/story)
            layout: Layout type (square/portrait/landscape)
            output_path: Path to save output image
            
        Returns:
            Path to created graphic
        """
        logger.info(f"Creating branded graphic for {newspaper} - {platform} {content_type}")
        
        # Get brand and platform specifications
        brand_specs = get_brand_specs(newspaper)
        platform_specs = get_platform_specs(platform, content_type, layout)
        
        if not brand_specs or not platform_specs:
            raise ValueError(f"Invalid specifications for {newspaper} or {platform}")
        
        # Load and resize input image
        image = self._load_and_resize_image(
            input_image_path,
            platform_specs["width"],
            platform_specs["height"]
        )
        
        # Convert to PIL Image for text operations
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Add text overlay
        pil_image = self._add_text_overlay(
            pil_image,
            heading_text,
            brand_specs,
            content_type
        )
        
        # Add logo (placeholder for now - logo loading to be implemented)
        # pil_image = self._add_logo(pil_image, brand_specs, content_type)
        
        # Save output
        pil_image.save(output_path, quality=95)
        logger.info(f"Branded graphic saved to {output_path}")
        
        return output_path
    
    def _load_and_resize_image(
        self,
        image_path: str,
        target_width: int,
        target_height: int
    ) -> np.ndarray:
        """Load and resize image to target dimensions."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Resize with aspect ratio preservation and cropping
        h, w = image.shape[:2]
        target_ratio = target_width / target_height
        current_ratio = w / h
        
        if current_ratio > target_ratio:
            # Image is wider than target
            new_width = int(h * target_ratio)
            start_x = (w - new_width) // 2
            image = image[:, start_x:start_x + new_width]
        else:
            # Image is taller than target
            new_height = int(w / target_ratio)
            start_y = (h - new_height) // 2
            image = image[start_y:start_y + new_height, :]
        
        # Resize to exact dimensions
        image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
        
        return image
    
    def _add_text_overlay(
        self,
        image: Image.Image,
        text: str,
        brand_specs,
        content_type: str
    ) -> Image.Image:
        """Add text overlay to image with brand styling."""
        draw = ImageDraw.Draw(image)
        
        # Get font size based on content type
        font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        
        # Try to load Axiforma font
        font = self._load_font(font_size)
        
        # Get text position based on brand specs
        title_location = (
            brand_specs.title_location_story if content_type == "story"
            else brand_specs.title_location_post
        )
        
        position = self._calculate_text_position(
            image.size,
            text,
            font,
            title_location
        )
        
        # Add main text
        draw.text(
            position,
            text,
            font=font,
            fill=brand_specs.font_color
        )
        
        return image
    
    def _calculate_text_position(
        self,
        image_size: Tuple[int, int],
        text: str,
        font: ImageFont,
        location: str
    ) -> Tuple[int, int]:
        """Calculate text position based on location specification."""
        width, height = image_size
        
        # Get text bounding box (approximate)
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            # Fallback for older PIL versions
            text_width = len(text) * 20
            text_height = 40
        
        margin = 40
        
        # Calculate position based on location
        positions = {
            "top-left": (margin, margin),
            "top-right": (width - text_width - margin, margin),
            "top-center": ((width - text_width) // 2, margin),
            "center": ((width - text_width) // 2, (height - text_height) // 2),
            "bottom-left": (margin, height - text_height - margin),
            "bottom-right": (width - text_width - margin, height - text_height - margin),
        }
        
        return positions.get(location, positions["top-left"])


# Create singleton instance
image_processing_service = ImageProcessingService()


