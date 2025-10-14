"""
Advanced graphic composition service for creating branded social media graphics.
Inspired by the example outputs provided by the user.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from typing import Optional, Tuple, Dict
from pathlib import Path
from loguru import logger

from models.brand_config import get_brand_specs, get_platform_specs
from assets.newspaper_colors import get_newspaper_colors_rgb


class GraphicComposer:
    """Advanced service for creating branded social media graphics."""
    
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
        
        # Add dark overlay for text readability
        canvas = self._add_dark_overlay(canvas, intensity=0.4)
        
        # Add campaign banner (top-right) only if campaign_type is not "none"
        if campaign_type != "none":
            canvas = self._add_campaign_banner(canvas, colors, campaign_type)
        
        # Add newspaper branding (top-left)
        canvas = self._add_newspaper_branding(canvas, newspaper, colors)
        
        # Add main headline
        canvas = self._add_headline(canvas, heading_text, target_width, target_height)
        
        # Add call-to-action button
        canvas = self._add_cta_button(canvas, colors, target_width, target_height)
        
        # Add newspaper footer branding
        canvas = self._add_footer_branding(canvas, newspaper, colors, target_height)
        
        # Add bottom CTA
        canvas = self._add_bottom_cta(canvas, colors, target_height)
        
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
            
            # Apply blur effect for better text readability
            image = image.filter(ImageFilter.GaussianBlur(radius=1))
            
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
    
    def _add_campaign_banner(self, canvas: Image.Image, colors: Dict, campaign_type: str) -> Image.Image:
        """Add campaign banner with custom text."""
        draw = ImageDraw.Draw(canvas)
        width, height = canvas.size
        
        # Use the provided campaign type as banner text
        # Convert to uppercase and add "2025" if not present
        banner_text = campaign_type.upper()
        if "2025" not in banner_text:
            banner_text += " 2025"
        
        # Calculate banner size and position
        banner_height = int(height * 0.08)  # 8% of canvas height
        banner_width = int(width * 0.4)     # 40% of canvas width
        
        # Position at top-right
        x_pos = width - banner_width - int(width * 0.05)  # 5% margin
        y_pos = int(height * 0.05)  # 5% margin
        
        # Create banner background
        banner_rect = [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height]
        draw.rectangle(banner_rect, fill=colors["primary"])
        
        # Add banner text
        font_size = min(banner_height // 2, 24)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), banner_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text in banner
        text_x = x_pos + (banner_width - text_width) // 2
        text_y = y_pos + (banner_height - text_height) // 2
        
        draw.text((text_x, text_y), banner_text, fill=colors["text_light"], font=font)
        
        return canvas
    
    def _add_newspaper_branding(self, canvas: Image.Image, newspaper: str, colors: Dict) -> Image.Image:
        """Add newspaper branding in top-left corner."""
        draw = ImageDraw.Draw(canvas)
        width, height = canvas.size
        
        # Branding area
        branding_width = int(width * 0.4)
        branding_height = int(height * 0.12)
        x_pos = int(width * 0.05)  # 5% margin
        y_pos = int(height * 0.05)  # 5% margin
        
        # Add newspaper name
        font_size = min(branding_height // 3, 32)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Newspaper name with styling
        newspaper_text = newspaper.upper()
        
        # Add text shadow
        draw.text((x_pos + 2, y_pos + 2), newspaper_text, fill=(0, 0, 0, 128), font=font)
        # Add main text
        draw.text((x_pos, y_pos), newspaper_text, fill=colors["text_light"], font=font)
        
        # Add "Sponsoroitu" text below
        sponsored_text = "Sponsoroitu"
        sponsored_font_size = font_size // 2
        try:
            sponsored_font = ImageFont.truetype("arial.ttf", sponsored_font_size)
        except:
            sponsored_font = ImageFont.load_default()
        
        sponsored_y = y_pos + branding_height // 2
        draw.text((x_pos, sponsored_y), sponsored_text, fill=colors["text_light"], font=sponsored_font)
        
        return canvas
    
    def _add_headline(self, canvas: Image.Image, text: str, width: int, height: int) -> Image.Image:
        """Add main headline text."""
        draw = ImageDraw.Draw(canvas)
        
        # Position in center
        x_center = width // 2
        y_center = height // 2
        
        # Font size based on canvas size
        font_size = min(width // 15, height // 15, 48)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
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
            
            # Add text shadow
            draw.text((text_x + 2, text_y + 2), line, fill=(0, 0, 0, 128), font=font)
            # Add main text
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    def _add_cta_button(self, canvas: Image.Image, colors: Dict, width: int, height: int) -> Image.Image:
        """Add call-to-action button."""
        draw = ImageDraw.Draw(canvas)
        
        # Button dimensions
        button_width = int(width * 0.6)
        button_height = int(height * 0.08)
        button_x = (width - button_width) // 2
        button_y = int(height * 0.65)
        
        # Button background
        button_rect = [button_x, button_y, button_x + button_width, button_y + button_height]
        draw.rectangle(button_rect, fill=colors["secondary"], outline=colors["primary"], width=2)
        
        # Button text
        cta_text = "TEE PAIKALLINEN VAALIKONE"
        font_size = min(button_height // 3, 20)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text in button
        bbox = draw.textbbox((0, 0), cta_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = button_x + (button_width - text_width) // 2
        text_y = button_y + (button_height - text_height) // 2
        
        draw.text((text_x, text_y), cta_text, fill=colors["primary"], font=font)
        
        return canvas
    
    def _add_footer_branding(self, canvas: Image.Image, newspaper: str, colors: Dict, height: int) -> Image.Image:
        """Add newspaper branding in footer area."""
        draw = ImageDraw.Draw(canvas)
        width = canvas.size[0]
        
        # Footer area
        footer_height = int(height * 0.15)
        footer_y = height - footer_height
        
        # Footer background
        footer_rect = [0, footer_y, width, height]
        draw.rectangle(footer_rect, fill=colors["primary"])
        
        # Newspaper name in footer
        font_size = min(footer_height // 4, 36)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        newspaper_text = newspaper.upper()
        bbox = draw.textbbox((0, 0), newspaper_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = footer_y + (footer_height - font_size) // 2
        
        draw.text((text_x, text_y), newspaper_text, fill=colors["text_light"], font=font)
        
        return canvas
    
    def _add_bottom_cta(self, canvas: Image.Image, colors: Dict, height: int) -> Image.Image:
        """Add bottom call-to-action."""
        draw = ImageDraw.Draw(canvas)
        width = canvas.size[0]
        
        # Bottom CTA button
        button_width = int(width * 0.4)
        button_height = int(height * 0.06)
        button_x = (width - button_width) // 2
        button_y = height - int(height * 0.03) - button_height
        
        # Button background
        button_rect = [button_x, button_y, button_x + button_width, button_y + button_height]
        draw.rectangle(button_rect, fill=colors["secondary"], outline=colors["accent"], width=1)
        
        # Button text
        cta_text = "Lue lisää"
        font_size = min(button_height // 3, 16)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Center text in button
        bbox = draw.textbbox((0, 0), cta_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = button_x + (button_width - text_width) // 2
        text_y = button_y + (button_height - text_height) // 2
        
        draw.text((text_x, text_y), cta_text, fill=colors["accent"], font=font)
        
        return canvas


# Create singleton instance
graphic_composer = GraphicComposer()
