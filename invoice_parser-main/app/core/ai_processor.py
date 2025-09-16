"""
AI Processing Service

Handles AI-powered invoice data extraction using Google Gemini
with structured output parsing and validation.
"""
import base64
import logging
from typing import Optional
from io import BytesIO
from PIL import Image

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.core.config import get_settings
from app.models.schemas import InvoiceDataSchema

# Configure logging
logger = logging.getLogger(__name__)

# Extraction prompt template
EXTRACTION_PROMPT = """
You are an expert at extracting structured data from Indian GST-compliant invoices. 

Analyze this invoice image and extract the following information accurately:

IMPORTANT INSTRUCTIONS:
1. Extract ALL visible text accurately
2. For GST invoices, focus on GSTIN numbers, HSN codes, and tax breakdowns
3. If a field is not visible or unclear, use null
4. For amounts, extract only numeric values (remove currency symbols)
5. Preserve the exact text for company names and addresses
6. If you see multiple pages or complex layouts, extract systematically
7. Pay special attention to tax calculations and ensure they add up correctly
8. Return ONLY the JSON object, no additional text or explanation

Analyze the invoice now:
"""


class AIProcessor:
    """AI-powered invoice data extraction service."""
    
    def __init__(self):
        """Initialize AI processor with configured models."""
        self.settings = get_settings()
        self._model: Optional[ChatGoogleGenerativeAI] = None
        self._parser: Optional[PydanticOutputParser] = None
        self._prompt_template: Optional[PromptTemplate] = None
        
    @property
    def model(self) -> ChatGoogleGenerativeAI:
        """Get or create AI model instance."""
        if self._model is None:
            try:
                self._model = ChatGoogleGenerativeAI(
                    model=self.settings.AI_MODEL_NAME,
                    temperature=self.settings.AI_TEMPERATURE,
                    google_api_key=self.settings.GOOGLE_API_KEY
                )
                logger.info(f"AI model {self.settings.AI_MODEL_NAME} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")
                raise
        return self._model
    
    @property
    def parser(self) -> PydanticOutputParser:
        """Get or create Pydantic output parser."""
        if self._parser is None:
            self._parser = PydanticOutputParser(pydantic_object=InvoiceDataSchema)
        return self._parser
    
    @property
    def prompt_template(self) -> PromptTemplate:
        """Get or create prompt template with parser instructions."""
        if self._prompt_template is None:
            self._prompt_template = PromptTemplate(
                template=EXTRACTION_PROMPT + "\n{format_instructions}",
                input_variables=[],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
        return self._prompt_template
    
    def is_available(self) -> bool:
        """Check if AI model is available."""
        try:
            return self.model is not None
        except Exception:
            return False
    
    def preprocess_image(self, image_data: bytes, content_type: str) -> Image.Image:
        """Preprocess image for AI processing."""
        try:
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                logger.info(f"Converted image from {image.mode} to RGB")
            
            logger.info(f"Image preprocessed: {image.size}, mode: {image.mode}")
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    async def extract_invoice_data(
        self, 
        image_data: bytes, 
        content_type: str
    ) -> tuple[InvoiceDataSchema, str]:
        """
        Extract structured data from invoice image.
        
        Args:
            image_data: Raw image bytes
            content_type: MIME type of the image
            
        Returns:
            Tuple of (extracted_data, raw_response)
            
        Raises:
            ValueError: If image processing fails
            Exception: If AI processing fails
        """
        try:
            # Preprocess image
            image = self.preprocess_image(image_data, content_type)
            
            # Create formatted prompt
            formatted_prompt = self.prompt_template.format()
            
            # Encode image for API
            image_base64 = base64.b64encode(image_data).decode()
            file_extension = content_type.split('/')[-1]
            
            # Create message with image and prompt
            message = HumanMessage(
                content=[
                    {"type": "text", "text": formatted_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{image_base64}"}}
                ]
            )
            
            # Generate content with AI model
            logger.info("Sending request to AI model for invoice extraction")
            response = self.model.invoke([message])
            raw_response = response.content.strip()
            
            logger.info(f"Received AI response: {len(raw_response)} characters")
            
            # Parse and validate response
            try:
                invoice_data = self.parser.parse(raw_response)
                invoice_data.raw_text = raw_response  # Store raw response
                
                logger.info(f"Successfully extracted invoice data: {invoice_data.invoice_number}")
                return invoice_data, raw_response
                
            except Exception as parse_error:
                logger.error(f"Failed to parse AI response: {parse_error}")
                # Return partial data with raw response for debugging
                fallback_data = InvoiceDataSchema(
                    raw_text=raw_response,
                    extraction_confidence="low"
                )
                return fallback_data, raw_response
                
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            raise
    
    def get_model_info(self) -> dict[str, any]:
        """Get information about the current AI model."""
        return {
            "model_name": self.settings.AI_MODEL_NAME,
            "temperature": self.settings.AI_TEMPERATURE,
            "available": self.is_available(),
            "provider": "Google Gemini"
        }
