"""
Newspaper color palettes extracted from frontend CSS.
Based on the newspaper brand colors found in frontend/src/App.css
"""

NEWSPAPER_COLORS = {
    "Kaleva": {
        "primary": "#FF8C30",      # Orange
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#FF8C30",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Lapin Kansa": {
        "primary": "#0075bf",      # Blue
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#0075bf",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Ilkka-Pohjalainen": {
        "primary": "#54c1ef",      # Light Blue
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#54c1ef",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Koillissanomat": {
        "primary": "#76bd22",      # Lime Green
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#76bd22",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Rantalakeus": {
        "primary": "#de3414",      # Red
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#de3414",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Iijokiseutu": {
        "primary": "#0073bb",      # Blue
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#0073bb",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Raahen Seutu": {
        "primary": "#76bd22",      # Lime Green (same as Koillissanomat)
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#76bd22",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Pyhäjokiseutu": {
        "primary": "#009ac1",      # Cyan
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#009ac1",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    },
    "Siikajokilaakso": {
        "primary": "#0073bb",      # Blue (same as Iijokiseutu)
        "secondary": "#FFFFFF",    # White
        "accent": "#000000",       # Black
        "background": "#0073bb",   # Primary as background
        "text_light": "#FFFFFF",   # White text
        "text_dark": "#000000"     # Black text
    }
}


def get_newspaper_colors(newspaper: str) -> dict:
    """Get color palette for a newspaper."""
    return NEWSPAPER_COLORS.get(newspaper, NEWSPAPER_COLORS["Kaleva"])


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_newspaper_colors_rgb(newspaper: str) -> dict:
    """Get color palette for a newspaper with RGB values."""
    colors = get_newspaper_colors(newspaper)
    rgb_colors = {}
    
    for key, hex_color in colors.items():
        rgb_colors[key] = hex_to_rgb(hex_color)
    
    return rgb_colors
