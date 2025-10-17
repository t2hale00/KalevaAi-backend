# Kaleva Media Content Generator - Backend

AI-assisted application for generating and adapting branded graphic campaign materials for Kaleva Media's social media channels.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Create Required Directories

The application will automatically create these directories on startup:
- `uploads/` - Temporary storage for uploaded images
- `outputs/` - Generated branded graphics
- `assets/` - Brand assets (logos, fonts)
- `logs/` - Application logs

### 4. Add Brand Assets

Place newspaper logos in `assets/logos/` directory:
- `kaleva.png`
- `lapin_kansa.png`
- `ilkka_pohjalainen.png`
- etc.

## Running the Backend

### Development Mode

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health Check
```
GET /api/health
```

### Generate Content
```
POST /api/generate
Content-Type: multipart/form-data

Form fields:
- platform: instagram|facebook|linkedin
- content_type: post|story
- layout: square|portrait|landscape
- output_type: static|animated
- newspaper: Kaleva|Lapin Kansa|etc.
- text_content: (optional) input text
- text_length: short|medium|long
- image: (optional) image file
```

### Download Generated Content
```
GET /api/download/{filename}
```

### List Available Newspapers
```
GET /api/newspapers
```

## Project Structure

```
backend/
├── api.py                    # Main FastAPI application
├── config.py                 # Configuration settings
├── models/
│   ├── schemas.py           # Pydantic request/response models
│   └── brand_config.py      # Brand specifications
├── services/
│   ├── text_generation.py   # Gemini text generation
│   ├── image_processing.py  # Static graphic creation
│   ├── video_generation.py  # Motion graphic creation
│   └── brand_service.py     # Brand management
├── workflows/
│   └── content_workflow.py  # Main orchestration workflow
├── utils/
│   ├── file_handler.py      # File operations
│   └── validators.py        # Input validation
└── tests/                   # Test files
```

## Technology Stack

- **FastAPI** - Web framework
- **Google Gemini** - AI text generation
- **Pillow** - Image processing
- **OpenCV** - Advanced image manipulation
- **MoviePy** - Video generation
- **Pydantic** - Data validation
- **Loguru** - Logging

## Platform Specifications

### Instagram
- Post: 1080×1080 (square), 1080×1350 (portrait)
- Story: 1080×1920 (portrait, MP4)

### Facebook
- Post: 1080×1080 (square), 1200×628 (landscape)
- Story: 1080×1920 (portrait, MP4)

### LinkedIn
- Post: 1200×627 (landscape)

## Development Notes

- Business logic and AI workflows are handled here, not in the frontend
- API endpoints fetch and process data; frontend displays results
- All brand specifications are defined in `models/brand_config.py`
- Gemini is used for all text generation tasks






