"""
Pydantic models for API request and response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class PlatformType(str, Enum):
    """Social media platform types."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


class ContentType(str, Enum):
    """Content type (post or story)."""
    POST = "post"
    STORY = "story"


class LayoutType(str, Enum):
    """Layout aspect ratios."""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class OutputType(str, Enum):
    """Output format type."""
    STATIC = "static"
    ANIMATED = "animated"


class NewspaperType(str, Enum):
    """Regional newspaper brands."""
    KALEVA = "Kaleva"
    LAPIN_KANSA = "Lapin Kansa"
    ILKKA_POHJALAINEN = "Ilkka-Pohjalainen"
    KOILLISSANOMAT = "Koillissanomat"
    RANTALAKEUS = "Rantalakeus"
    IIJOKISEUTU = "Iijokiseutu"
    RAAHEN_SEUTU = "Raahen Seutu"
    PYHAJOKISEUTU = "Pyhäjokiseutu"
    SIIKAJOKILAAKSO = "Siikajokilaakso"


class TextLength(str, Enum):
    """Text generation length options."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    text_content: Optional[str] = Field(None, description="Input text for content generation")
    platform: PlatformType = Field(..., description="Target social media platform")
    content_type: ContentType = Field(..., description="Content type (post or story)")
    layout: LayoutType = Field(..., description="Layout aspect ratio")
    output_type: OutputType = Field(..., description="Static or animated output")
    newspaper: NewspaperType = Field(..., description="Regional newspaper brand")
    text_length: TextLength = Field(TextLength.MEDIUM, description="Generated text length")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_content": "Join us for our summer campaign!",
                "platform": "instagram",
                "content_type": "post",
                "layout": "square",
                "output_type": "static",
                "newspaper": "Kaleva",
                "text_length": "medium"
            }
        }


class GeneratedText(BaseModel):
    """Generated text content."""
    heading: str = Field(..., description="Generated heading/title")
    description: str = Field(..., description="Generated description/post copy")
    platform: str = Field(..., description="Target platform")
    tone: str = Field(..., description="Text tone")


class MultipleGeneratedText(BaseModel):
    """Multiple versions of generated text content."""
    headings: List[str] = Field(..., description="List of generated headings")
    descriptions: List[str] = Field(..., description="List of generated descriptions")
    platform: str = Field(..., description="Target platform")
    tone: str = Field(..., description="Text tone")


class ContentGenerationResponse(BaseModel):
    """Response model for content generation."""
    success: bool = Field(..., description="Whether generation was successful")
    task_id: str = Field(..., description="Unique task identifier")
    generated_text: GeneratedText = Field(..., description="Generated text content")
    graphic_url: Optional[str] = Field(None, description="URL to download generated graphic")
    graphic_urls: Optional[List[str]] = Field(None, description="URLs to download all generated graphics")
    file_format: str = Field(..., description="Output file format (PNG, JPEG, MP4)")
    dimensions: str = Field(..., description="Output dimensions")
    message: Optional[str] = Field(None, description="Additional message or error details")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    gemini_configured: bool = Field(..., description="Whether Gemini API is configured")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


