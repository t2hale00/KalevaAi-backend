# Font Loading Instructions

## Current Status
The system now properly searches for Axiforma font in multiple locations:

1. **Local assets directory**: `backend/assets/fonts/Axiforma.ttf` or `Axiforma.otf`
2. **System fonts (Windows)**: `C:/Windows/Fonts/Axiforma.ttf`
3. **System fonts (macOS)**: `/System/Library/Fonts/Axiforma.ttf`
4. **System fonts (Linux)**: `/usr/share/fonts/truetype/axiforma.ttf`

## To Use Axiforma Font

### Option 1: Add Font File to Assets
1. Obtain the Axiforma font file from Kaleva Media
2. Place it in `backend/assets/fonts/` as:
   - `Axiforma.ttf` or `Axiforma.otf`

### Option 2: Install System-Wide
1. Install Axiforma font on your system
2. The system will automatically find it in system font directories

## Current Fallback Chain
If Axiforma is not found, the system falls back to:
1. Arial (Windows)
2. Helvetica (macOS) 
3. PIL default font (final fallback)

## Testing
To test font loading, check the logs for:
- `"Loaded font: [path]"` - Axiforma found and loaded
- `"Using Arial fallback font"` - Using Arial fallback
- `"Using PIL default font"` - Using default fallback

