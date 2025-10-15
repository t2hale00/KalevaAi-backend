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
            # Local assets directory - direct files
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family}.ttf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family}.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family.lower()}.ttf",
            Path(__file__).parent.parent / "assets" / "fonts" / f"{font_family.lower()}.otf",
            # Local assets directory - Axiforma Complete Family
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} Regular.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} Medium.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} Bold.otf",
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
        campaign_type: str = "elections_2025",
        version: int = 1,
        banner_text: str = None
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
        
        # Use layout handlers for different content types and layouts
        from services.layouts import PostLayoutHandler, StoryLayoutHandler, LandscapeLayoutHandler
        
        if content_type == "post" and layout in ["portrait", "square"]:
            # Use PostLayoutHandler for Portrait/Square posts
            post_handler = PostLayoutHandler(self)
            canvas = post_handler.create_portrait_post(canvas, heading_text, newspaper, content_type, 
                                                     campaign_type, colors, target_width, target_height, version, banner_text)
        
        elif content_type == "story":
            # Use StoryLayoutHandler for stories
            story_handler = StoryLayoutHandler(self)
            if layout in ["portrait", "square"]:
                canvas = story_handler.create_portrait_story(canvas, heading_text, newspaper, content_type, 
                                                          campaign_type, colors, target_width, target_height, version, banner_text)
            else:  # landscape
                canvas = story_handler.create_landscape_story(canvas, heading_text, newspaper, content_type, 
                                                            campaign_type, colors, target_width, target_height, banner_text)
        
        elif layout == "landscape":
            # Use LandscapeLayoutHandler for landscape posts
            landscape_handler = LandscapeLayoutHandler(self)
            canvas = landscape_handler.create_landscape_post(canvas, heading_text, newspaper, content_type, 
                                                           campaign_type, colors, target_width, target_height)
        
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
        """Add newspaper logo in top-right corner with proper color template."""
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
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo with color template to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas
    
    def _add_newspaper_background_overlay(self, canvas: Image.Image, colors: Dict, width: int, height: int) -> Image.Image:
        """Add solid newspaper color background at bottom like in the example."""
        # Create solid background covering bottom 1/3 of the image
        overlay_height = height // 3
        
        # Create solid overlay (not semi-transparent)
        overlay = Image.new('RGB', (width, overlay_height), colors["primary"])
        
        # Position at bottom
        y_pos = height - overlay_height
        
        # Paste solid overlay onto canvas
        canvas.paste(overlay, (0, y_pos))
        
        return canvas
    
    def _add_semi_transparent_overlay(self, canvas: Image.Image, colors: Dict, width: int, height: int) -> Image.Image:
        """Add semi-transparent overlay transitioning to solid background (Version 1 style)."""
        # Create overlay covering bottom 2/3 of the image
        overlay_height = int(height * 0.67)  # 2/3 of canvas height
        
        # Create semi-transparent overlay that transitions to solid
        overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 0))
        
        # Create gradient from transparent to solid newspaper color
        for y in range(overlay_height):
            # Calculate alpha value (0 = transparent at top, 255 = solid at bottom)
            alpha = int(255 * (y / overlay_height))
            
            # Create horizontal line with gradient alpha
            line_color = (*colors["primary"], alpha)
            for x in range(width):
                overlay.putpixel((x, y), line_color)
        
        # Position at bottom
        y_pos = height - overlay_height
        
        # Paste overlay onto canvas
        canvas = canvas.convert('RGBA')
        canvas.paste(overlay, (0, y_pos), overlay)
        
        return canvas.convert('RGB')
    
    def _add_newspaper_logo_bottom(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo at bottom center like in the example."""
        # Calculate logo size and position
        logo_height = int(height * 0.08)  # 8% of canvas height
        
        # Position at bottom center
        x_center = width // 2
        y_pos = height - int(height * 0.05) - logo_height  # 5% margin from bottom
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo to fit the height
                    logo_width = int(logo_height * (logo.width / logo.height))
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Center horizontally
                    x_pos = x_center - logo_width // 2
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo at bottom center to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas
    
    def _add_headline_top(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add headline at top of image (Version 2 - KALEVA style)."""
        draw = ImageDraw.Draw(canvas)
        
        # Position at top center
        x_center = width // 2
        y_pos = int(height * 0.1)  # 10% from top
        
        # Get font size from brand specifications
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        else:
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
        start_y = y_pos
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x_center - text_width // 2
            text_y = start_y + (i * font_size)
            
            # Use yellow color for Version 2 (like KALEVA example)
            draw.text((text_x, text_y), line, fill=(255, 255, 0), font=font)  # Yellow
        
        return canvas
    
    def _add_newspaper_logo_bottom_left(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo at bottom left (Version 2 - KALEVA style)."""
        # Calculate logo size and position
        logo_height = int(height * 0.08)  # 8% of canvas height
        
        # Position at bottom left
        x_pos = int(width * 0.05)  # 5% margin from left
        y_pos = height - int(height * 0.05) - logo_height  # 5% margin from bottom
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo to fit the height
                    logo_width = int(logo_height * (logo.width / logo.height))
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo at bottom left to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas
    
    def _apply_color_template(self, logo: Image.Image, colors: Dict) -> Image.Image:
        """Apply newspaper color template to logo."""
        # Convert logo to RGBA if not already
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Create a new image with the same size
        colored_logo = Image.new('RGBA', logo.size, (0, 0, 0, 0))
        
        # Get logo data
        logo_data = logo.getdata()
        colored_data = []
        
        for pixel in logo_data:
            r, g, b, a = pixel
            
            # If pixel is not transparent
            if a > 0:
                # Convert to grayscale to determine intensity
                intensity = (r + g + b) / 3
                
                # Apply newspaper primary color based on intensity
                if intensity > 128:  # Light areas
                    # Use primary color for light areas
                    new_r = colors["primary"][0]
                    new_g = colors["primary"][1] 
                    new_b = colors["primary"][2]
                else:  # Dark areas
                    # Use secondary color for dark areas
                    new_r = colors["secondary"][0]
                    new_g = colors["secondary"][1]
                    new_b = colors["secondary"][2]
                
                colored_data.append((new_r, new_g, new_b, a))
            else:
                # Keep transparent pixels transparent
                colored_data.append((0, 0, 0, 0))
        
        # Put the colored data back
        colored_logo.putdata(colored_data)
        
        return colored_logo
    
    def _add_campaign_banner(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int, banner_text: str = None) -> Image.Image:
        """Add campaign banner with user-entered title."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
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
    
    def _add_headline(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add main headline text using brand specifications."""
        draw = ImageDraw.Draw(canvas)
        
        # Position to overlap photo and background overlay (like in the example)
        x_center = width // 2
        # Position text so it spans across the transition from photo to background overlay
        y_center = height - (height // 3) + (height // 6)  # Position in the middle of the overlay area
        
        # Get font size from brand specifications (80px for stories, 60px for posts)
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        else:
            # Fallback to canvas-based sizing
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
    
    
    


    def _add_campaign_banner_story(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int, banner_text: str = None) -> Image.Image:
        """Add campaign banner in upper-right for stories."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
        # Calculate banner size
        banner_height = int(height * 0.08)  # 8% of canvas height
        banner_width = int(width * 0.35)    # 35% of canvas width
        
        # Position in upper-right for stories
        x_pos = width - banner_width - int(width * 0.05)  # 5% margin from right
        y_pos = int(height * 0.05)  # 5% margin from top
        
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
    
    def _add_headline_centered(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add headline centered on image (Version 2 story style)."""
        draw = ImageDraw.Draw(canvas)
        
        # Position in center of image
        x_center = width // 2
        y_center = height // 2
        
        # Get font size from brand specifications
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        else:
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
            
            # Use white color for stories
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    def _add_campaign_banner_landscape(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int, banner_text: str = None) -> Image.Image:
        """Add campaign banner in upper-left of photo section for landscape."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
        # Calculate banner size
        banner_height = int(height * 0.08)  # 8% of canvas height
        banner_width = int(width * 0.25)   # 25% of canvas width (smaller for landscape)
        
        # Position in upper-left of photo section (left ~70% of canvas)
        photo_width = int(width * 0.7)  # Photo takes ~70% of width
        x_pos = int(photo_width * 0.05)  # 5% margin from left edge of photo section
        y_pos = int(height * 0.05)  # 5% margin from top
        
        # Create banner background
        banner_rect = [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height]
        draw.rectangle(banner_rect, fill=colors["primary"])
        
        # Add banner text
        font_size = min(banner_height // 2, 20)
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
    
    def _create_split_screen_layout(self, canvas: Image.Image, colors: Dict, width: int, height: int) -> Image.Image:
        """Create split-screen layout with solid color panel on right."""
        draw = ImageDraw.Draw(canvas)
        
        # Calculate split positions
        photo_width = int(width * 0.7)  # Photo takes ~70% of width
        panel_width = width - photo_width  # Solid color panel takes remaining ~30%
        
        # Create solid color panel on the right
        panel_rect = [photo_width, 0, width, height]
        draw.rectangle(panel_rect, fill=colors["primary"])
        
        return canvas
    
    def _add_headline_landscape(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add headline on solid color panel (right side) for landscape."""
        draw = ImageDraw.Draw(canvas)
        
        # Calculate panel positions
        photo_width = int(width * 0.7)  # Photo takes ~70% of width
        panel_width = width - photo_width  # Solid color panel takes remaining ~30%
        
        # Position on solid color panel
        x_center = photo_width + (panel_width // 2)  # Center of right panel
        y_pos = int(height * 0.2)  # 20% from top
        
        # Get font size from brand specifications
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
        else:
            font_size = min(panel_width // 8, height // 15, 48)
        
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
            
            if text_width > panel_width * 0.9:  # 90% of panel width
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
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x_center - text_width // 2
            text_y = y_pos + (i * font_size)
            
            # Use white color for landscape
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    def _add_newspaper_logo_landscape(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo on solid color panel (right side, bottom) for landscape."""
        # Calculate panel positions
        photo_width = int(width * 0.7)  # Photo takes ~70% of width
        panel_width = width - photo_width  # Solid color panel takes remaining ~30%
        
        # Calculate logo size and position
        logo_height = int(height * 0.08)  # 8% of canvas height
        
        # Position at bottom of solid color panel
        x_center = photo_width + (panel_width // 2)  # Center of right panel
        y_pos = height - int(height * 0.1) - logo_height  # 10% margin from bottom
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo to fit the height
                    logo_width = int(logo_height * (logo.width / logo.height))
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Center horizontally on panel
                    x_pos = x_center - logo_width // 2
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo to landscape graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas


# Create singleton instance
graphic_composer = GraphicComposer()
