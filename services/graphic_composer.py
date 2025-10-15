"""
Advanced graphic composition service for creating branded social media graphics.
Inspired by the example outputs provided by the user.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Dict
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs, get_platform_specs
from assets.newspaper_colors import get_newspaper_colors_rgb


class GraphicComposer:
    """Advanced service for creating branded social media graphics."""
    
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
    
    def create_branded_social_graphic(
        self,
        input_image_path: str,
        heading_text: str,
        description_text: str,
        newspaper: str,
        platform: str,
        content_type: str,
        layout: str,
        output_path: str,
        campaign_type: str = "elections_2025"
    ) -> str:
        """
        Create a complete branded social media graphic like the examples.
        
        Args:
            input_image_path: Path to background image
            heading_text: Main headline text
            description_text: Description/subtitle text
            newspaper: Newspaper brand
            platform: Social media platform
            content_type: post or story
            layout: square, portrait, landscape
            output_path: Output file path
            campaign_type: Type of campaign (e.g., "elections_2025")
            
        Returns:
            Path to created graphic
        """
        logger.info(f"Creating branded social graphic for {newspaper}")
        
        # Get specifications
        platform_specs = get_platform_specs(platform, content_type, layout)
        colors = get_newspaper_colors_rgb(newspaper)
        
        if not platform_specs:
            raise ValueError(f"Invalid platform configuration: {platform}/{content_type}/{layout}")
        
        target_width = platform_specs["width"]
        target_height = platform_specs["height"]
        
        # Create base canvas
        canvas = Image.new('RGB', (target_width, target_height), color=colors["secondary"])
        
        # Load and process background image
        if input_image_path and Path(input_image_path).exists():
            background = self._create_background_layer(input_image_path, target_width, target_height)
            canvas.paste(background, (0, 0))
        
        # Add campaign banner with correct positioning
        canvas = self._add_campaign_banner(canvas, colors, content_type, target_width, target_height)
        
        # Add newspaper logo (top-right)
        canvas = self._add_newspaper_logo(canvas, newspaper, colors)
        
        # Add main headline
        canvas = self._add_headline(canvas, heading_text, target_width, target_height)
        
        # Save the final image
        canvas.save(output_path, quality=95, optimize=True)
        logger.info(f"Branded graphic saved to {output_path}")
        
        return output_path
    
    def _create_background_layer(self, image_path: str, width: int, height: int) -> Image.Image:
        """Create processed background layer."""
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Keep photo clear without blur effects
            
            # Resize with smart cropping
            image = self._smart_resize(image, width, height)
            
            return image
        except Exception as e:
            logger.warning(f"Could not load background image: {e}")
            # Return a gradient background
            return self._create_gradient_background(width, height)
    
    def _smart_resize(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize image with smart cropping to maintain aspect ratio."""
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        current_ratio = img_width / img_height
        
        if current_ratio > target_ratio:
            # Image is wider than target
            new_height = target_height
            new_width = int(target_height * current_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop horizontally
            x_offset = (new_width - target_width) // 2
            image = image.crop((x_offset, 0, x_offset + target_width, target_height))
        else:
            # Image is taller than target
            new_width = target_width
            new_height = int(target_width / current_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop vertically
            y_offset = (new_height - target_height) // 2
            image = image.crop((0, y_offset, target_width, y_offset + target_height))
        
        return image
    
    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """Create a gradient background when no image is provided."""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create a subtle gradient
        for y in range(height):
            color_value = int(240 - (y / height) * 40)  # Gradient from light to darker
            color = (color_value, color_value, color_value)
            draw.line([(0, y), (width, y)], fill=color)
        
        return image
    
    def _add_dark_overlay(self, canvas: Image.Image, intensity: float = 0.4) -> Image.Image:
        """Add dark overlay for better text readability."""
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, int(255 * intensity)))
        canvas = canvas.convert('RGBA')
        canvas = Image.alpha_composite(canvas, overlay)
        return canvas.convert('RGB')
    
    def _add_newspaper_logo(self, canvas: Image.Image, newspaper: str, colors: Dict) -> Image.Image:
        """Add newspaper logo in top-right corner."""
        width, height = canvas.size
        
        # Calculate logo size and position
        logo_size = int(height * 0.08)  # 8% of canvas height
        
        # Position at top-right
        x_pos = width - logo_size - int(width * 0.05)  # 5% margin
        y_pos = int(height * 0.05)  # 5% margin
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo to fit the size
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas
    
    def _add_campaign_banner(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int) -> Image.Image:
        """Add campaign banner with correct positioning based on content type."""
        draw = ImageDraw.Draw(canvas)
        
        # Campaign banner text
        banner_text = "ALUE- JA KUNTA-VAALIT 2025"
        
        # Calculate banner size
        banner_height = int(height * 0.08)  # 8% of canvas height
        banner_width = int(width * 0.35)    # 35% of canvas width
        
        # Position based on content type
        if content_type == "story":
            # Stories: upper right
            x_pos = width - banner_width - int(width * 0.05)  # 5% margin
            y_pos = int(height * 0.05)  # 5% margin
        else:
            # Posts: upper left
            x_pos = int(width * 0.05)  # 5% margin
            y_pos = int(height * 0.05)  # 5% margin
        
        # Create banner background
        banner_rect = [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height]
        draw.rectangle(banner_rect, fill=colors["primary"])
        
        # Add banner text
        font_size = min(banner_height // 2, 24)
        font = self._load_font(font_size)
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), banner_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text in banner
        text_x = x_pos + (banner_width - text_width) // 2
        text_y = y_pos + (banner_height - text_height) // 2
        
        draw.text((text_x, text_y), banner_text, fill=colors["text_light"], font=font)
        
        return canvas
    
    def _add_headline(self, canvas: Image.Image, text: str, width: int, height: int) -> Image.Image:
        """Add main headline text."""
        draw = ImageDraw.Draw(canvas)
        
        # Position in center
        x_center = width // 2
        y_center = height // 2
        
        # Font size based on canvas size
        font_size = min(width // 15, height // 15, 48)
        font = self._load_font(font_size)
        
        # Wrap text if needed
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_text = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > width * 0.8:  # 80% of canvas width
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Draw each line
        total_height = len(lines) * font_size
        start_y = y_center - total_height // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x_center - text_width // 2
            text_y = start_y + (i * font_size)
            
            # Add main text with clear visibility
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    
    


# Create singleton instance
graphic_composer = GraphicComposer()
