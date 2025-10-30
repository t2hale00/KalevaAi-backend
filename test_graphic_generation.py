#!/usr/bin/env python3
"""
Test script for graphic generation functionality.
This script tests the complete graphic generation pipeline.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.graphic_composer import graphic_composer
from services.text_generation import text_generation_service
from assets.newspaper_colors import get_newspaper_colors
import numpy as np
from PIL import Image

def create_test_image(width: int = 1080, height: int = 1080) -> str:
    """Create a test background image."""
    # Create a simple gradient image
    image = Image.new('RGB', (width, height))
    
    # Create gradient
    for y in range(height):
        for x in range(width):
            # Create a subtle gradient
            r = int(100 + (x / width) * 155)
            g = int(150 + (y / height) * 105)
            b = int(200 + ((x + y) / (width + height)) * 55)
            image.putpixel((x, y), (r, g, b))
    
    # Save test image
    test_image_path = backend_dir / "test_background.jpg"
    image.save(test_image_path, quality=90)
    return str(test_image_path)

def test_color_palettes():
    """Test newspaper color palettes."""
    print("🎨 Testing newspaper color palettes...")
    
    newspapers = ["Kaleva", "Lapin Kansa", "Koillissanomat", "Raahen Seutu"]
    
    for newspaper in newspapers:
        colors = get_newspaper_colors(newspaper)
        print(f"  {newspaper}: {colors['primary']}")
    
    print("✅ Color palettes loaded successfully")

def test_graphic_generation():
    """Test the graphic generation."""
    print("\n🖼️  Testing graphic generation...")
    
    # Create test background
    test_image_path = create_test_image()
    print(f"  Created test background: {test_image_path}")
    
    # Test parameters
    newspapers = ["Kaleva", "Lapin Kansa", "Koillissanomat"]
    platforms = ["instagram", "facebook", "linkedin"]
    
    output_dir = backend_dir / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_tests = 0
    
    for newspaper in newspapers:
        for platform in platforms:
            for layout in ["square", "portrait", "landscape"]:
                # Skip invalid combinations
                if platform == "linkedin" and layout != "landscape":
                    continue
                if platform in ["instagram", "facebook"] and layout == "landscape" and platform == "instagram":
                    continue
                
                total_tests += 1
                
                try:
                    output_filename = f"test_{newspaper}_{platform}_{layout}.png"
                    output_path = output_dir / output_filename
                    
                    # Test headline and description
                    headline = f"Test headline for {newspaper}"
                    description = f"Test description for {newspaper} {platform} {layout}"
                    
                    # Generate graphic
                    graphic_composer.create_branded_social_graphic(
                        input_image_path=test_image_path,
                        heading_text=headline,
                        description_text=description,
                        newspaper=newspaper,
                        platform=platform,
                        content_type="post",
                        layout=layout,
                        output_path=str(output_path),
                        campaign_type="elections_2025"
                    )
                    
                    print(f"  ✅ Generated: {output_filename}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed {newspaper} {platform} {layout}: {e}")
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} graphics generated successfully")
    
    # Clean up test image
    try:
        os.remove(test_image_path)
        print(f"  🗑️  Cleaned up test background")
    except:
        pass
    
    return success_count == total_tests

def test_text_generation():
    """Test text generation (if Gemini is configured)."""
    print("\n📝 Testing text generation...")
    
    try:
        # Test text generation
        result = text_generation_service.generate_text(
            platform="instagram",
            content_type="post",
            text_length="medium",
            input_text="Test input for elections",
            newspaper="Kaleva"
        )
        
        print(f"  ✅ Generated heading: {result['heading']}")
        print(f"  ✅ Generated description: {result['description']}")
        return True
        
    except Exception as e:
        print(f"  ⚠️  Text generation test failed: {e}")
        print("  This is expected if GEMINI_API_KEY is not configured")
        return False

def main():
    """Run all tests."""
    print("🧪 Kaleva Media Graphic Generation Test Suite")
    print("=" * 50)
    
    # Test color palettes
    test_color_palettes()
    
    # Test graphic generation
    graphic_success = test_graphic_generation()
    
    # Test text generation
    text_success = test_text_generation()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  Color Palettes: ✅")
    print(f"  Graphic Generation: {'✅' if graphic_success else '❌'}")
    print(f"  Text Generation: {'✅' if text_success else '⚠️ (requires Gemini API)'}")
    
    if graphic_success:
        print("\n🎉 Core functionality working!")
        print("📁 Check backend/test_outputs/ for generated graphics")
        print("\nNext steps:")
        print("1. Add newspaper logos to backend/assets/logos/")
        print("2. Configure GEMINI_API_KEY for text generation")
        print("3. Test with real images")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return graphic_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






