"""
Brand configuration and specifications for regional newspapers.
Based on Table 2 from aim.md: Brand & Regional Newspaper Design Adaptation Specifications
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class BrandSpecs:
    """Brand specifications for a regional newspaper."""
    name: str
    logo_path: str  # Path to logo file in assets folder
    color_palette: List[str]  # Hex color codes
    font_family: str
    font_color: str
    font_size_story: int  # Font size for stories (px)
    font_size_post: int   # Font size for posts (px)
    title_location_post: str  # "top-left", "top-right", etc.
    title_location_story: str


# Brand specifications for each newspaper
BRAND_SPECIFICATIONS: Dict[str, BrandSpecs] = {
    "Kaleva": BrandSpecs(
        name="Kaleva",
        logo_path="assets/logos/kaleva.png",
        color_palette=["#000000", "#FFFFFF"],  # Black and white
        font_family="Axiforma",
        font_color="#FFFFFF",  # White
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Lapin Kansa": BrandSpecs(
        name="Lapin Kansa",
        logo_path="assets/logos/lapin_kansa.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Ilkka-Pohjalainen": BrandSpecs(
        name="Ilkka-Pohjalainen",
        logo_path="assets/logos/ilkka_pohjalainen.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Koillissanomat": BrandSpecs(
        name="Koillissanomat",
        logo_path="assets/logos/koillissanomat.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Rantalakeus": BrandSpecs(
        name="Rantalakeus",
        logo_path="assets/logos/rantalakeus.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Iijokiseutu": BrandSpecs(
        name="Iijokiseutu",
        logo_path="assets/logos/iijokiseutu.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Raahen Seutu": BrandSpecs(
        name="Raahen Seutu",
        logo_path="assets/logos/raahen_seutu.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Pyhäjokiseutu": BrandSpecs(
        name="Pyhäjokiseutu",
        logo_path="assets/logos/pyhajokiseutu.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
    
    "Siikajokilaakso": BrandSpecs(
        name="Siikajokilaakso",
        logo_path="assets/logos/siikajokilaakso.png",
        color_palette=["#000000", "#FFFFFF"],
        font_family="Axiforma",
        font_color="#FFFFFF",
        font_size_story=80,
        font_size_post=60,
        title_location_post="top-left",
        title_location_story="top-right"
    ),
}


# Platform technical specifications from Table 1
PLATFORM_SPECIFICATIONS = {
    "instagram": {
        "post": {
            "square": {"width": 1080, "height": 1080, "aspect_ratio": "1:1", "format": ["PNG", "JPEG"]},
            "portrait": {"width": 1080, "height": 1350, "aspect_ratio": "4:5", "format": ["PNG", "JPEG"]},
        },
        "story": {
            "portrait": {"width": 1080, "height": 1920, "aspect_ratio": "9:16", "format": ["MP4"], "max_length": 60},
        },
    },
    "facebook": {
        "post": {
            "square": {"width": 1080, "height": 1080, "aspect_ratio": "1:1", "format": ["PNG", "JPEG"]},
            "landscape": {"width": 1200, "height": 628, "aspect_ratio": "1.91:1", "format": ["PNG", "JPEG"]},
        },
        "story": {
            "portrait": {"width": 1080, "height": 1920, "aspect_ratio": "9:16", "format": ["MP4"], "max_length": 60},
        },
    },
    "linkedin": {
        "post": {
            "landscape": {"width": 1200, "height": 627, "aspect_ratio": "1.91:1", "format": ["PNG", "JPEG"]},
        },
    },
}


def get_brand_specs(newspaper: str) -> BrandSpecs:
    """Get brand specifications for a newspaper."""
    return BRAND_SPECIFICATIONS.get(newspaper)


def get_platform_specs(platform: str, content_type: str, layout: str) -> dict:
    """Get platform specifications for content generation."""
    return PLATFORM_SPECIFICATIONS.get(platform, {}).get(content_type, {}).get(layout, {})


