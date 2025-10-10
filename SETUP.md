# Backend Setup Guide

## Quick Start

### 1. Create a `.env` file in the backend directory

Create a file named `.env` in the `backend/` folder with the following content:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro

# Application Settings
DEBUG=True

# File Upload Settings
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
ASSETS_DIR=assets
```

**Important:** Replace `your_gemini_api_key_here` with your actual Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Create Assets Directory

The application will create most directories automatically, but you can prepare the assets folder:

```bash
mkdir -p assets/logos
```

### 4. Run the Backend

```bash
python api.py
```

Or with auto-reload:

```bash
uvicorn api:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### 5. Test the API

Visit http://localhost:8000/docs to see the interactive API documentation and test endpoints.

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

## Next Steps

- Add newspaper logos to `assets/logos/`
- Configure CORS origins in `.env` if your frontend runs on different ports
- Review `config.py` for additional configuration options

