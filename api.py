"""
FastAPI application for Kaleva Media content generation.
Main API endpoints for the backend.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
from loguru import logger
import sys

from config import settings
from models.schemas import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    HealthCheckResponse,
    ErrorResponse
)
from workflows.content_workflow import content_workflow
from utils.file_handler import file_handler
from utils.validators import content_validator

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/api.log", rotation="500 MB", level="DEBUG")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-assisted branded content generation for Kaleva Media"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    gemini_configured = bool(settings.GEMINI_API_KEY)
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        gemini_configured=gemini_configured
    )


@app.post("/api/generate", response_model=ContentGenerationResponse)
async def generate_content(
    platform: str = Form(...),
    content_type: str = Form(...),
    layout: str = Form(...),
    output_type: str = Form(...),
    newspaper: str = Form(...),
    text_content: Optional[str] = Form(None),
    text_length: str = Form("medium"),
    image: Optional[UploadFile] = File(None)
):
    """
    Generate branded content with text and graphics.
    
    This endpoint receives form data and returns generated content.
    """
    logger.info(f"Received content generation request: {platform}/{content_type}/{layout}")
    
    try:
        # Validate request
        is_valid, error_message = content_validator.validate_content_request(
            platform=platform,
            content_type=content_type,
            layout=layout,
            newspaper=newspaper
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Handle image upload
        image_path = None
        if image:
            # Validate file type
            if not file_handler.validate_file_type(image.filename, "image"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image format. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
                )
            
            # Save uploaded image
            image_content = await image.read()
            image_path = await file_handler.save_upload(image_content, image.filename)
            logger.info(f"Image uploaded: {image_path}")
        
        # Create request object
        request = ContentGenerationRequest(
            text_content=text_content,
            platform=platform,
            content_type=content_type,
            layout=layout,
            output_type=output_type,
            newspaper=newspaper,
            text_length=text_length
        )
        
        # Generate content
        response = await content_workflow.generate_content(request, image_path)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download generated content file.
    
    Args:
        filename: Name of file to download
    """
    file_path = file_handler.get_file_path(filename, directory="output")
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if filename.endswith('.mp4'):
        media_type = "video/mp4"
    elif filename.endswith('.png'):
        media_type = "image/png"
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        media_type = "image/jpeg"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@app.get("/api/newspapers")
async def list_newspapers():
    """Get list of available newspapers."""
    from services.brand_service import brand_service
    return {
        "newspapers": brand_service.list_available_newspapers()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


