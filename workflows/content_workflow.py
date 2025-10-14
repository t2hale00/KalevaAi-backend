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
        image_path: Optional[str] = None,
        banner_data: Optional[dict] = None
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
            # Step 1: Generate multiple versions of text content
            logger.info("Step 1: Generating multiple versions of text content")
            generated_text_dict = text_generation_service.generate_text(
                platform=request.platform.value,
                content_type=request.content_type.value,
                text_length=request.text_length.value,
                input_text=request.text_content,
                newspaper=request.newspaper.value,
                num_versions=2
            )
            
            headings = generated_text_dict["headings"]
            descriptions = generated_text_dict["descriptions"]
            
            logger.info(f"Generated {len(headings)} headings and {len(descriptions)} descriptions")
            
            # Step 2: Get platform specifications
            platform_specs = brand_service.get_platform_requirements(
                request.platform.value,
                request.content_type.value,
                request.layout.value
            )
            
            # Step 3: Generate graphic (static or animated)
            logger.info(f"Step 2: Generating {request.output_type.value} graphic")
            
            # Initialize variables
            graphic_url = None
            graphic_urls = []
            file_format = "N/A"
            
            if image_path is None:
                # Create a placeholder if no image provided (for testing)
                logger.warning("No image provided, using placeholder")
                # Variables already initialized above
            elif request.output_type.value == "static":
                # Generate multiple static graphics (2 headings × 2 descriptions = 4 graphics)
                logger.info("Step 2: Generating multiple static graphics")
                
                # Determine campaign type based on banner data
                campaign_type = "none"
                if banner_data and banner_data.get("add_banner") and banner_data.get("banner_name"):
                    campaign_type = banner_data["banner_name"]
                
                graphic_urls = []
                graphic_count = 0
                
                for i, heading in enumerate(headings):
                    for j, description in enumerate(descriptions):
                        graphic_count += 1
                        output_filename = f"{task_id}_v{graphic_count}.png"
                        output_path = str(self.output_dir / output_filename)
                        
                        try:
                            graphic_composer.create_branded_social_graphic(
                                input_image_path=image_path,
                                heading_text=heading,
                                description_text=description,
                                newspaper=request.newspaper.value,
                                platform=request.platform.value,
                                content_type=request.content_type.value,
                                layout=request.layout.value,
                                output_path=output_path,
                                campaign_type=campaign_type
                            )
                            
                            graphic_urls.append(f"/api/download/{output_filename}")
                            logger.info(f"Generated graphic {graphic_count}: {output_filename}")
                            
                        except Exception as e:
                            logger.error(f"Error generating graphic {graphic_count}: {e}")
                
                # Return all graphic URLs
                graphic_url = graphic_urls[0] if graphic_urls else None
                file_format = "PNG"
            else:
                # Generate animated graphic (use first heading for now)
                output_filename = f"{task_id}.mp4"
                output_path = str(self.output_dir / output_filename)
                
                # Use the first heading for animated graphics
                first_heading = headings[0] if headings else "Generated Heading"
                
                video_generation_service.create_motion_graphic(
                    input_image_path=image_path,
                    heading_text=first_heading,
                    newspaper=request.newspaper.value,
                    platform=request.platform.value,
                    content_type=request.content_type.value,
                    layout=request.layout.value,
                    output_path=output_path
                )
                
                graphic_url = f"/api/download/{output_filename}"
                file_format = "MP4"
                graphic_urls = [graphic_url]  # Single video for now
            
            # Create response with multiple versions
            dimensions = f"{platform_specs['width']}×{platform_specs['height']}px ({platform_specs['aspect_ratio']})"
            
            # Create multiple GeneratedText objects for each combination
            generated_texts = []
            
            # Ensure we have headings and descriptions
            if not headings:
                headings = ["Generated Heading"]
            if not descriptions:
                descriptions = ["Generated Description"]
            
            for i, heading in enumerate(headings):
                for j, description in enumerate(descriptions):
                    text_obj = GeneratedText(
                        heading=heading,
                        description=description,
                        platform=request.platform.value,
                        tone="professional" if request.platform.value == "linkedin" else "friendly"
                    )
                    generated_texts.append(text_obj)
            
            # For now, return the first text version (we'll update frontend to handle multiple)
            primary_generated_text = generated_texts[0] if generated_texts else GeneratedText(
                heading="Generated Heading",
                description="Generated Description",
                platform=request.platform.value,
                tone="friendly"
            )
            
            response = ContentGenerationResponse(
                success=True,
                task_id=task_id,
                generated_text=primary_generated_text,
                graphic_url=graphic_url,
                graphic_urls=graphic_urls if graphic_urls else ([graphic_url] if graphic_url else []),
                file_format=file_format,
                dimensions=dimensions,
                message=f"Generated {len(headings)} headings, {len(descriptions)} descriptions, and {len(graphic_urls)} graphics successfully"
            )
            
            logger.info(f"Workflow completed successfully - Task ID: {task_id}")
            return response
            
        except Exception as e:
            logger.error(f"Workflow failed - Task ID: {task_id}: {str(e)}")
            raise


# Create singleton instance
content_workflow = ContentWorkflow()


