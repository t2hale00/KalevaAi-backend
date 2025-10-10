"""
Main content workflow orchestration.
Coordinates text generation, image processing, and video generation.
"""
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4
from loguru import logger

from services.text_generation import text_generation_service
from services.image_processing import image_processing_service
from services.video_generation import video_generation_service
from services.graphic_composer import graphic_composer
from services.brand_service import brand_service
from models.schemas import ContentGenerationRequest, ContentGenerationResponse, GeneratedText
from config import settings


class ContentWorkflow:
    """Main workflow for generating branded content."""
    
    def __init__(self):
        """Initialize workflow."""
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_content(
        self,
        request: ContentGenerationRequest,
        image_path: Optional[str] = None
    ) -> ContentGenerationResponse:
        """
        Main workflow to generate branded content.
        
        Args:
            request: Content generation request
            image_path: Path to uploaded image (if any)
            
        Returns:
            Content generation response with generated text and graphic URL
        """
        task_id = str(uuid4())
        logger.info(f"Starting content generation workflow - Task ID: {task_id}")
        
        try:
            # Step 1: Generate text content using Gemini
            logger.info("Step 1: Generating text content")
            generated_text_dict = text_generation_service.generate_text(
                platform=request.platform.value,
                content_type=request.content_type.value,
                text_length=request.text_length.value,
                input_text=request.text_content,
                newspaper=request.newspaper.value
            )
            
            generated_text = GeneratedText(
                heading=generated_text_dict["heading"],
                description=generated_text_dict["description"],
                platform=request.platform.value,
                tone="professional" if request.platform.value == "linkedin" else "friendly"
            )
            
            logger.info(f"Generated text - Heading: {generated_text.heading[:50]}...")
            
            # Step 2: Get platform specifications
            platform_specs = brand_service.get_platform_requirements(
                request.platform.value,
                request.content_type.value,
                request.layout.value
            )
            
            # Step 3: Generate graphic (static or animated)
            logger.info(f"Step 2: Generating {request.output_type.value} graphic")
            
            if image_path is None:
                # Create a placeholder if no image provided (for testing)
                logger.warning("No image provided, using placeholder")
                # In production, you might want to create a default branded background
                graphic_url = None
                file_format = "N/A"
            elif request.output_type.value == "static":
                # Generate static graphic using advanced composer
                output_filename = f"{task_id}.png"
                output_path = str(self.output_dir / output_filename)
                
                graphic_composer.create_branded_social_graphic(
                    input_image_path=image_path,
                    heading_text=generated_text.heading,
                    description_text=generated_text.description,
                    newspaper=request.newspaper.value,
                    platform=request.platform.value,
                    content_type=request.content_type.value,
                    layout=request.layout.value,
                    output_path=output_path,
                    campaign_type="elections_2025"
                )
                
                graphic_url = f"/api/download/{output_filename}"
                file_format = "PNG"
            else:
                # Generate animated graphic
                output_filename = f"{task_id}.mp4"
                output_path = str(self.output_dir / output_filename)
                
                video_generation_service.create_motion_graphic(
                    input_image_path=image_path,
                    heading_text=generated_text.heading,
                    newspaper=request.newspaper.value,
                    platform=request.platform.value,
                    content_type=request.content_type.value,
                    layout=request.layout.value,
                    output_path=output_path
                )
                
                graphic_url = f"/api/download/{output_filename}"
                file_format = "MP4"
            
            # Create response
            dimensions = f"{platform_specs['width']}×{platform_specs['height']}px ({platform_specs['aspect_ratio']})"
            
            response = ContentGenerationResponse(
                success=True,
                task_id=task_id,
                generated_text=generated_text,
                graphic_url=graphic_url,
                file_format=file_format,
                dimensions=dimensions,
                message="Content generated successfully"
            )
            
            logger.info(f"Workflow completed successfully - Task ID: {task_id}")
            return response
            
        except Exception as e:
            logger.error(f"Workflow failed - Task ID: {task_id}: {str(e)}")
            raise


# Create singleton instance
content_workflow = ContentWorkflow()


