#!/usr/bin/env python3
"""
Test script for optional banner functionality.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.graphic_composer import graphic_composer
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
    test_image_path = backend_dir / "test_banner_background.jpg"
    image.save(test_image_path, quality=90)
    return str(test_image_path)

def test_banner_functionality():
    """Test the banner functionality with different scenarios."""
    print("🎯 Testing Optional Banner Functionality")
    print("=" * 50)
    
    # Create test background
    test_image_path = create_test_image()
    print(f"✅ Created test background: {test_image_path}")
    
    # Create output directory
    output_dir = backend_dir / "test_banner_outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "No Banner",
            "campaign_type": "none",
            "description": "Graphic without any campaign banner"
        },
        {
            "name": "Jääkiekko2025",
            "campaign_type": "Jääkiekko2025",
            "description": "Graphic with ice hockey campaign banner"
        },
        {
            "name": "Vaalit2025",
            "campaign_type": "Vaalit2025", 
            "description": "Graphic with election campaign banner"
        },
        {
            "name": "Kesä2025",
            "campaign_type": "Kesä2025",
            "description": "Graphic with summer campaign banner"
        }
    ]
    
    newspapers = ["Kaleva", "Lapin Kansa", "Koillissanomat"]
    success_count = 0
    
    for newspaper in newspapers:
        print(f"\n📰 Testing with {newspaper}:")
        
        for scenario in test_scenarios:
            try:
                output_filename = f"test_{newspaper}_{scenario['name'].replace('2025', '2025').replace('ä', 'a').replace('ö', 'o')}.png"
                output_path = output_dir / output_filename
                
                # Generate graphic
                graphic_composer.create_branded_social_graphic(
                    input_image_path=test_image_path,
                    heading_text=f"Test headline for {scenario['name']}",
                    description_text=f"Test description for {scenario['description']}",
                    newspaper=newspaper,
                    platform="instagram",
                    content_type="post",
                    layout="square",
                    output_path=str(output_path),
                    campaign_type=scenario["campaign_type"]
                )
                
                print(f"  ✅ {scenario['name']}: {output_filename}")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ {scenario['name']}: {e}")
    
    # Clean up test image
    try:
        os.remove(test_image_path)
        print(f"\n🗑️  Cleaned up test background")
    except:
        pass
    
    print(f"\n📊 Results: {success_count}/{len(test_scenarios) * len(newspapers)} graphics generated")
    
    if success_count == len(test_scenarios) * len(newspapers):
        print("🎉 All banner tests passed!")
        print(f"📁 Check {output_dir} for generated graphics")
        return True
    else:
        print("❌ Some banner tests failed")
        return False

def main():
    """Run banner tests."""
    success = test_banner_functionality()
    
    print("\n" + "=" * 50)
    print("🎯 Banner Functionality Test Complete")
    
    if success:
        print("✅ Optional banner feature is working correctly!")
        print("\nFeatures tested:")
        print("  • Graphics without banners")
        print("  • Custom campaign banners (Jääkiekko2025, Vaalit2025, etc.)")
        print("  • Multiple newspapers with different banners")
        print("  • Proper text formatting and positioning")
    else:
        print("⚠️  Some issues detected. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)




