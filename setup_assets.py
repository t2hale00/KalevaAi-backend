#!/usr/bin/env python3
"""
Setup script to copy newspaper logos from frontend to backend assets.
Run this script to set up the brand assets for the backend.
"""
import shutil
from pathlib import Path
import sys
import os

def setup_assets():
    """Copy logos from frontend to backend assets directory."""
    
    # Define paths
    backend_dir = Path(__file__).parent
    frontend_dir = backend_dir.parent / "frontend"
    assets_dir = backend_dir / "assets"
    logos_dir = assets_dir / "logos"
    
    # Create directories
    assets_dir.mkdir(exist_ok=True)
    logos_dir.mkdir(exist_ok=True)
    
    # Frontend logos directory
    frontend_logos = frontend_dir / "src" / "logos" / "black"
    
    if not frontend_logos.exists():
        print(f"❌ Frontend logos directory not found: {frontend_logos}")
        print("Please make sure the frontend logos are in the correct location.")
        return False
    
    print("📁 Setting up newspaper logos...")
    
    # Logo mapping (frontend filename -> backend filename)
    logo_files = {
        "kalevablack.png": "kaleva.png",
        "lapinkansablack.png": "lapin_kansa.png", 
        "ilkkapohjolainenblack.png": "ilkka_pohjalainen.png",
        "koillissanomatblack.png": "koillissanomat.png",
        "rantalakeusblack.png": "rantalakeus.png",
        "iijokiseutublack.png": "iijokiseutu.png",
        "raahenseutublack.png": "raahen_seutu.png",
        "pyhäjokiseutublack.png": "pyhajokiseutu.png",
        "siikajokilaaksoblack.png": "siikajokilaakso.png"
    }
    
    copied_count = 0
    
    for frontend_file, backend_file in logo_files.items():
        src_path = frontend_logos / frontend_file
        dst_path = logos_dir / backend_file
        
        if src_path.exists():
            try:
                shutil.copy2(src_path, dst_path)
                print(f"✅ Copied: {frontend_file} -> {backend_file}")
                copied_count += 1
            except Exception as e:
                print(f"❌ Error copying {frontend_file}: {e}")
        else:
            print(f"⚠️  Not found: {frontend_file}")
    
    print(f"\n📊 Summary: {copied_count}/{len(logo_files)} logos copied successfully")
    
    if copied_count == len(logo_files):
        print("🎉 All logos copied successfully!")
        return True
    else:
        print("⚠️  Some logos were not copied. Check the messages above.")
        return False

def create_sample_fonts():
    """Create sample font files (placeholder for now)."""
    fonts_dir = Path(__file__).parent / "assets" / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    # Create a README for fonts
    readme_content = """# Fonts Directory

This directory should contain the newspaper brand fonts.

## Required Fonts

For each newspaper, you may need:
- Axiforma (mentioned in brand specs)
- Custom newspaper fonts

## Getting Fonts

1. Contact Kaleva Media for official brand fonts
2. Or use system fonts as fallback (currently implemented)

## Current Implementation

The system currently uses:
- Arial as fallback font
- System default fonts when custom fonts are not available

This works for testing but for production, proper brand fonts should be added.
"""
    
    readme_path = fonts_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📝 Created font setup guide: {readme_path}")

if __name__ == "__main__":
    print("🚀 Setting up Kaleva Media backend assets...")
    print("=" * 50)
    
    success = setup_assets()
    create_sample_fonts()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Asset setup completed successfully!")
        print("\nNext steps:")
        print("1. Add proper brand fonts to backend/assets/fonts/")
        print("2. Test the graphic generation")
        print("3. Customize campaign elements as needed")
    else:
        print("⚠️  Asset setup completed with some issues.")
        print("Please check the messages above and fix any problems.")
    
    sys.exit(0 if success else 1)
