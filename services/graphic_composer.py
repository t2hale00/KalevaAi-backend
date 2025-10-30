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
    
    def _load_font(self, font_size: int, font_family: str = "Axiforma", weight: str = "Bold") -> ImageFont.FreeTypeFont:
        """Load font with proper fallback chain, prioritizing Bold weight for headings."""
        # Try to load Axiforma from various possible locations
        possible_paths = [
            # Local assets directory - Axiforma Complete Family (prioritize Bold)
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} {weight}.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} Medium.otf",
            Path(__file__).parent.parent / "assets" / "fonts" / "Axiforma Complete Family" / "Axiforma Complete Family" / f"Kastelov - {font_family} Regular.otf",
            # Local assets directory - direct files
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
            if layout == "landscape":
                # For landscape layouts, photo takes 3/5 of width
                photo_width = int(target_width * 0.6)  # 3/5 of width
                background = self._create_background_layer(input_image_path, photo_width, target_height)
                
                if version == 1:
                    # Version 1: Photo on the right (solid panel on left)
                    canvas.paste(background, (int(target_width * 0.4), 0))  # Start at 2/5 position
                else:
                    # Version 2: Photo on the left (solid panel on right)
                    canvas.paste(background, (0, 0))
            else:
                # For portrait/square layouts
                if version == 2:
                    # Version 2: Photo covers entire canvas
                    background = self._create_background_layer(input_image_path, target_width, target_height)
                    canvas.paste(background, (0, 0))
                else:
                    # Version 1: Photo covers top 80% (updated from 82%)
                    photo_height = int(target_height * 0.80)
                    background = self._create_background_layer(input_image_path, target_width, photo_height)
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
                                                            campaign_type, colors, target_width, target_height, version, banner_text)
        
        elif layout == "landscape":
            # Use LandscapeLayoutHandler for landscape posts
            landscape_handler = LandscapeLayoutHandler(self)
            canvas = landscape_handler.create_landscape_post(canvas, heading_text, newspaper, content_type, 
                                                          campaign_type, colors, target_width, target_height, version, banner_text)
        
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
        """Add solid newspaper color background covering bottom 20% (Version 1 style)."""
        # Create overlay covering bottom 20% of the image (solid newspaper color)
        overlay_height = int(height * 0.20)  # 20% of canvas height
        
        # Create solid newspaper color background
        overlay = Image.new('RGB', (width, overlay_height), colors["primary"])
        
        # Position at bottom
        y_pos = height - overlay_height
        
        # Paste solid overlay onto canvas
        canvas.paste(overlay, (0, y_pos))
        
        return canvas
    
    def _add_newspaper_logo_bottom_story(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo at bottom center for stories (higher positioning)."""
        draw = ImageDraw.Draw(canvas)
        
        # Calculate logo size and position with uniform sizing
        logo_height = int(height * 0.12)  # 12% of canvas height (increased from 8%)
        max_logo_width = int(width * 0.5)  # Maximum 50% of canvas width for uniform sizing (increased from 40%)
        
        # Calculate solid color area (bottom 20%)
        solid_color_height = int(height * 0.20)
        solid_color_start = height - solid_color_height
        
        # Position logo in top area of solid color section (stories only)
        x_center = width // 2
        # Move logo to top 1/5 of solid color area for stories (higher positioning)
        y_center = solid_color_start + (solid_color_height // 5)  # Top 1/5 of solid color
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo with uniform sizing constraints
                    # Calculate aspect ratio
                    aspect_ratio = logo.width / logo.height
                    
                    # Calculate width based on height constraint
                    logo_width = int(logo_height * aspect_ratio)
                    
                    # If width exceeds maximum, scale down proportionally
                    if logo_width > max_logo_width:
                        logo_width = max_logo_width
                        logo_height = int(logo_width / aspect_ratio)
                    
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_center - logo.width // 2, y_center - logo.height // 2), logo)
                    logger.info(f"Added {newspaper} logo at bottom center to story graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        # Fallback: Add text-based logo if image logo failed
        if not (brand_specs and brand_specs.logo_path and Path(brand_specs.logo_path).exists()):
            # Use newspaper name as text logo
            font_size = min(logo_height, 24)
            font = self._load_font(font_size, weight="Bold")
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), newspaper, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position text logo in center of solid color area
            text_x = x_center - text_width // 2
            text_y = y_center - text_height // 2
            
            # Add text shadow for better readability
            shadow_offset = 1
            draw.text((text_x + shadow_offset, text_y + shadow_offset), newspaper, fill=(0, 0, 0), font=font)
            
            # Add main text
            draw.text((text_x, text_y), newspaper, fill=colors["text_light"], font=font)
            logger.info(f"Added {newspaper} text logo at bottom center to story graphic")
        
        return canvas
        
    def _add_newspaper_logo_bottom(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo at bottom center like in the example."""
        # Calculate logo size and position with uniform sizing
        logo_height = int(height * 0.08)  # 8% of canvas height (original size for posts)
        max_logo_width = int(width * 0.4)  # Maximum 40% of canvas width for uniform sizing (original for posts)
        
        # Calculate solid color area (bottom 20%)
        solid_color_height = int(height * 0.20)
        solid_color_start = height - solid_color_height
        
        # Position logo in center of solid color area (original positioning for posts)
        x_center = width // 2
        y_center = solid_color_start + (solid_color_height // 2)  # Center of solid color area
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo with uniform sizing constraints
                    # Calculate aspect ratio
                    aspect_ratio = logo.width / logo.height
                    
                    # Calculate width based on height constraint
                    logo_width = int(logo_height * aspect_ratio)
                    
                    # If width exceeds maximum, scale down proportionally
                    if logo_width > max_logo_width:
                        logo_width = max_logo_width
                        logo_height = int(logo_width / aspect_ratio)
                    
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_center - logo.width // 2, y_center - logo.height // 2), logo)
                    logger.info(f"Added {newspaper} logo at bottom center to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        # Fallback: Add text-based logo if image logo failed
        if not (brand_specs and brand_specs.logo_path and Path(brand_specs.logo_path).exists()):
            # Use newspaper name as text logo
            font_size = min(logo_height, 24)
            font = self._load_font(font_size, weight="Bold")
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), newspaper, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position text logo in center of solid color area
            text_x = x_center - text_width // 2
            text_y = y_center - text_height // 2
            
            # Add text shadow for better readability
            shadow_offset = 1
            draw.text((text_x + shadow_offset, text_y + shadow_offset), newspaper, fill=(0, 0, 0), font=font)
            
            # Add main text
            draw.text((text_x, text_y), newspaper, fill=colors["text_light"], font=font)
            logger.info(f"Added {newspaper} text logo at bottom center to graphic")
        
        return canvas
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo with uniform sizing constraints
                    # Calculate aspect ratio
                    aspect_ratio = logo.width / logo.height
                    
                    # Calculate width based on height constraint
                    logo_width = int(logo_height * aspect_ratio)
                    
                    # If width exceeds maximum, scale down proportionally
                    if logo_width > max_logo_width:
                        logo_width = max_logo_width
                        logo_height = int(logo_width / aspect_ratio)
                    
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if needed for transparency
                    if logo.mode != 'RGBA':
                        logo = logo.convert('RGBA')
                    
                    # Apply newspaper color template to logo
                    logo = self._apply_color_template(logo, colors)
                    
                    # Center horizontally and vertically in solid color area
                    x_pos = x_center - logo_width // 2
                    y_pos = y_center - logo_height // 2
                    
                    # Paste logo onto canvas
                    canvas.paste(logo, (x_pos, y_pos), logo)
                    logger.info(f"Added {newspaper} logo at bottom center to graphic")
                except Exception as e:
                    logger.warning(f"Failed to load logo for {newspaper}: {e}")
        
        return canvas
    
    def _add_headline_top(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add headline at top of image (Version 2 - KALEVA style)."""
        draw = ImageDraw.Draw(canvas)
        
        # Position at top center, but lower to avoid campaign banner overlap
        x_center = width // 2
        y_pos = int(height * 0.25)  # 25% from top (moved down from 18%)
        
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
            
            # Add text shadow for better readability
            shadow_offset = 2
            draw.text((text_x + shadow_offset, text_y + shadow_offset), line, fill=(0, 0, 0), font=font)
            
            # Use white color for Version 2 (clearer than yellow)
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)  # White
        
        return canvas
    
    def _add_newspaper_logo_bottom_left(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int) -> Image.Image:
        """Add newspaper logo at bottom left (Version 2 - KALEVA style)."""
        # Calculate logo size and position with uniform sizing
        # Make logo reach half of the width but with height constraint
        logo_width = int(width * 0.5)  # 50% of canvas width
        max_logo_height = int(height * 0.12)  # Maximum 12% of canvas height
        
        # Position at bottom left
        x_pos = int(width * 0.05)  # 5% margin from left
        y_pos = height - int(height * 0.05) - max_logo_height  # 5% margin from bottom
        
        # Try to load newspaper logo
        brand_specs = get_brand_specs(newspaper)
        if brand_specs and brand_specs.logo_path:
            logo_path = Path(brand_specs.logo_path)
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize logo with uniform sizing constraints
                    # Calculate aspect ratio
                    aspect_ratio = logo.width / logo.height
                    
                    # Calculate height based on width constraint
                    logo_height_calculated = int(logo_width / aspect_ratio)
                    
                    # If height exceeds maximum, scale down proportionally
                    if logo_height_calculated > max_logo_height:
                        logo_height_calculated = max_logo_height
                        logo_width = int(logo_height_calculated * aspect_ratio)
                    
                    logo = logo.resize((logo_width, logo_height_calculated), Image.Resampling.LANCZOS)
                    
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
        
        # Fallback: Add text-based logo if image logo failed
        if not (brand_specs and brand_specs.logo_path and Path(brand_specs.logo_path).exists()):
            # Use newspaper name as text logo
            draw = ImageDraw.Draw(canvas)
            font_size = min(max_logo_height, 24)
            font = self._load_font(font_size, weight="Bold")
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), newspaper, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position text logo at bottom left
            text_x = x_pos
            text_y = height - int(height * 0.05) - text_height  # 5% margin from bottom
            
            # Add text shadow for better readability
            shadow_offset = 1
            draw.text((text_x + shadow_offset, text_y + shadow_offset), newspaper, fill=(0, 0, 0), font=font)
            
            # Add main text (use newspaper primary color instead of white)
            draw.text((text_x, text_y), newspaper, fill=colors["primary"], font=font)
            logger.info(f"Added {newspaper} text logo at bottom left to graphic")
        
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
        """Add rectangular campaign banner with centered title and white background."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
        # Convert text to uppercase
        banner_text = banner_text.upper()
        
        # Calculate font size first to determine banner size
        font_size = min(int(height * 0.04), 28)  # 4% of height or max 28px
        font = self._load_font(font_size, weight="Bold")
        
        # Get text bounding box to calculate banner dimensions
        bbox = draw.textbbox((0, 0), banner_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate banner size with larger padding to ensure text fits comfortably
        padding_x = max(int(height * 0.04), 15)  # 4% of height or minimum 15px
        padding_y = max(int(height * 0.04), 10)  # 4% of height or minimum 10px
        banner_width = text_width + (padding_x * 2)
        banner_height = text_height + (padding_y * 2)
        
        # Center the banner horizontally on the canvas
        x_pos = (width - banner_width) // 2
        
        # Position banner above headlines based on content type
        # Stories: headlines at 50% mark, Posts: headlines at 25-60% depending on version
        if content_type == "story":
            # Position above centered headline (50% mark)
            y_pos = int(height * 0.50) - banner_height - int(height * 0.03)  # 3% gap above headline
        else:
            # Position above top headline (25% mark for v2, 60% for v1)
            # Position just above the higher headline to work for both versions
            y_pos = int(height * 0.25) - banner_height - int(height * 0.02)  # 2% gap above headline at 25%
        
        # Draw white background rectangle
        draw.rectangle(
            [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height],
            fill=(255, 255, 255),  # White background
            outline=None
        )
        
        # Calculate text position (centered in the banner)
        text_x = x_pos + padding_x
        text_y = y_pos + padding_y
        
        # Add main text with newspaper primary color
        draw.text((text_x, text_y), banner_text, fill=colors["primary"], font=font)
        
        return canvas
    
    def _add_headline(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str) -> Image.Image:
        """Add main headline text using brand specifications."""
        draw = ImageDraw.Draw(canvas)
        
        # Position text in lower part of photo area
        x_center = width // 2
        # Position text based on content type
        if content_type == "story":
            y_center = int(height * 0.50)  # Stories: Position at 50% mark
        else:
            y_center = int(height * 0.60)  # Posts: Position at 60% mark (higher)
        
        # Get font size from brand specifications (80px for stories, 60px for posts)
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
            # Increase font size for stories to make it bigger and bolder
            if content_type == "story":
                font_size = int(font_size * 1.2)  # 20% larger for stories
        else:
            # Fallback to canvas-based sizing
            font_size = min(width // 15, height // 15, 48)
        
        # Load bold font for better visibility
        font = self._load_font(font_size, weight="Bold")
        
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
            
            # Add text shadow for better readability
            shadow_offset = 2
            draw.text((text_x + shadow_offset, text_y + shadow_offset), line, fill=(0, 0, 0), font=font)
            
            # Add main text with clear visibility
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    
    


    def _add_campaign_banner_story(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int, banner_text: str = None) -> Image.Image:
        """Add rectangular campaign banner with centered title and white background for stories."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
        # Convert text to uppercase
        banner_text = banner_text.upper()
        
        # Calculate font size first to determine banner size
        font_size = min(int(height * 0.04), 28)  # 4% of height or max 28px
        font = self._load_font(font_size, weight="Bold")
        
        # Get text bounding box to calculate banner dimensions
        bbox = draw.textbbox((0, 0), banner_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate banner size with larger padding to ensure text fits comfortably
        padding_x = max(int(height * 0.04), 15)  # 4% of height or minimum 15px
        padding_y = max(int(height * 0.04), 10)  # 4% of height or minimum 10px
        banner_width = text_width + (padding_x * 2)
        banner_height = text_height + (padding_y * 2)
        
        # Center the banner horizontally on the canvas
        x_pos = (width - banner_width) // 2
        
        # Position banner above headlines for stories (headlines at 50% mark, centered)
        # Move banner much higher to avoid overlap with large headline text
        y_pos = int(height * 0.50) - banner_height - int(height * 0.12)  # 12% gap above headline to prevent overlap
        
        # Draw white background rectangle
        draw.rectangle(
            [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height],
            fill=(255, 255, 255),  # White background
            outline=None
        )
        
        # Calculate text position (centered in the banner)
        text_x = x_pos + padding_x
        text_y = y_pos + padding_y
        
        # Add main text with newspaper primary color
        draw.text((text_x, text_y), banner_text, fill=colors["primary"], font=font)
        
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
    
    def _add_campaign_banner_landscape(self, canvas: Image.Image, colors: Dict, content_type: str, width: int, height: int, banner_text: str = None, version: int = 2) -> Image.Image:
        """Add campaign banner in upper-left of photo section for landscape."""
        draw = ImageDraw.Draw(canvas)
        
        # Use user-entered banner text or default
        if not banner_text:
            banner_text = "ALUE- JA KUNTA-VAALIT 2025"  # Default fallback
        
        # Convert text to uppercase
        banner_text = banner_text.upper()
        
        # Calculate font size first to determine banner size
        font_size = min(int(height * 0.04), 28)  # 4% of height or max 28px
        font = self._load_font(font_size, weight="Bold")
        
        # Get text bounding box to calculate banner dimensions
        bbox = draw.textbbox((0, 0), banner_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate banner size with larger padding to ensure text fits comfortably
        padding_x = max(int(height * 0.04), 15)  # 4% of height or minimum 15px
        padding_y = max(int(height * 0.04), 10)  # 4% of height or minimum 10px
        banner_width = text_width + (padding_x * 2)
        banner_height = text_height + (padding_y * 2)
        
        # Position in upper-left of photo section
        panel_width = int(width * 0.4)  # 2/5 of width for solid color panel
        photo_width = width - panel_width  # Remaining 3/5 for photo
        
        if version == 1:
            # Version 1: Photo is on the right, banner goes in upper-left of photo section
            x_pos = photo_width + int(photo_width * 0.05)  # 5% margin from left edge of photo section
        else:
            # Version 2: Photo is on the left, banner goes in upper-left of photo section
            x_pos = int(photo_width * 0.05)  # 5% margin from left edge of photo section
        
        y_pos = int(height * 0.05)  # 5% margin from top
        
        # Create banner background with white background
        banner_rect = [x_pos, y_pos, x_pos + banner_width, y_pos + banner_height]
        draw.rectangle(banner_rect, fill=(255, 255, 255))
        
        # Center text within banner
        text_x = x_pos + padding_x
        text_y = y_pos + padding_y
        
        # Add banner text with newspaper primary color
        draw.text((text_x, text_y), banner_text, fill=colors["primary"], font=font)
        
        return canvas
    
    def _create_split_screen_layout(self, canvas: Image.Image, colors: Dict, width: int, height: int, version: int = 2) -> Image.Image:
        """Create split-screen layout with solid color panel on left (v1) or right (v2)."""
        draw = ImageDraw.Draw(canvas)
        
        # Calculate split positions - solid color takes 2/5, photo takes 3/5
        panel_width = int(width * 0.4)  # 2/5 of width for solid color panel
        photo_width = width - panel_width  # Remaining 3/5 for photo
        
        if version == 1:
            # Version 1: Solid color panel on the left
            panel_rect = [0, 0, panel_width, height]
        else:
            # Version 2: Solid color panel on the right (default)
            panel_rect = [photo_width, 0, width, height]
        
        draw.rectangle(panel_rect, fill=colors["primary"])
        
        return canvas
    
    def _add_headline_landscape(self, canvas: Image.Image, text: str, width: int, height: int, newspaper: str, content_type: str, version: int = 2) -> Image.Image:
        """Add headline on solid color panel for landscape (left for v1, right for v2)."""
        draw = ImageDraw.Draw(canvas)
        
        # Calculate panel positions - solid color takes 2/5, photo takes 3/5
        panel_width = int(width * 0.4)  # 2/5 of width for solid color panel
        photo_width = width - panel_width  # Remaining 3/5 for photo
        
        # Position on solid color panel
        if version == 1:
            # Version 1: Solid color panel on the left
            x_center = panel_width // 2  # Center of left panel
        else:
            # Version 2: Solid color panel on the right
            x_center = photo_width + (panel_width // 2)  # Center of right panel
        
        y_pos = int(height * 0.15)  # 15% from top (moved up to give more space)
        
        # Get font size from brand specifications
        brand_specs = get_brand_specs(newspaper)
        if brand_specs:
            # Use larger font sizes for landscape layout
            base_font_size = brand_specs.font_size_story if content_type == "story" else brand_specs.font_size_post
            font_size = min(base_font_size, panel_width // 8, height // 12, 48)
        else:
            # Larger default font size for landscape
            font_size = min(panel_width // 8, height // 12, 48)
        
        # Wrap text if needed with better margins
        # Calculate available text width with margins
        margin_percentage = 0.15  # 15% margin on each side
        available_width = panel_width * (1 - (margin_percentage * 2))  # 70% of panel width
        
        # First, check if we need to reduce font size for very long words
        words = text.split()
        font = self._load_font(font_size)
        for word in words:
            word_bbox = draw.textbbox((0, 0), word, font=font)
            word_width = word_bbox[2] - word_bbox[0]
            if word_width > available_width:
                # Reduce font size until the longest word fits
                while font_size > 12 and word_width > available_width:
                    font_size -= 1
                    font = self._load_font(font_size)
                    word_bbox = draw.textbbox((0, 0), word, font=font)
                    word_width = word_bbox[2] - word_bbox[0]
        
        # Now wrap text with the adjusted font size
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_text = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_text, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Check if text fits in available width
            if text_width > available_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Draw each line with better spacing
        line_spacing = int(font_size * 0.2)  # 20% of font size for line spacing
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x_center - text_width // 2
            text_y = y_pos + (i * (font_size + line_spacing))
            
            # Use white color for landscape
            draw.text((text_x, text_y), line, fill=(255, 255, 255), font=font)
        
        return canvas
    
    def _add_newspaper_logo_landscape(self, canvas: Image.Image, newspaper: str, colors: Dict, width: int, height: int, version: int = 2) -> Image.Image:
        """Add newspaper logo on solid color panel for landscape (left for v1, right for v2)."""
        # Calculate panel positions - solid color takes 2/5, photo takes 3/5
        panel_width = int(width * 0.4)  # 2/5 of width for solid color panel
        photo_width = width - panel_width  # Remaining 3/5 for photo
        
        # Calculate logo size and position - larger for better visibility
        logo_height = int(height * 0.08)  # 8% of canvas height (increased from 5%)
        
        # Position at bottom of solid color panel
        if version == 1:
            # Version 1: Solid color panel on the left
            x_center = panel_width // 2  # Center of left panel
        else:
            # Version 2: Solid color panel on the right
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
