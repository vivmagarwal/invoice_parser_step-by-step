from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import json
import base64
from PIL import Image
import io
from datetime import datetime
import random
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
import google.generativeai as genai


# Pydantic models for structured output
class InvoiceItem(BaseModel):
    """Individual line item from an invoice"""
    description: str = Field(description="Description of the item")
    quantity: float = Field(description="Quantity of the item")
    unit_price: float = Field(description="Unit price of the item")
    total: float = Field(description="Total price for this item")


class InvoiceData(BaseModel):
    """Structured invoice data extracted by AI"""
    invoice_number: Optional[str] = Field(description="Invoice number", default=None)
    invoice_date: Optional[str] = Field(description="Invoice date in YYYY-MM-DD format", default=None)
    due_date: Optional[str] = Field(description="Due date in YYYY-MM-DD format", default=None)

    vendor_name: Optional[str] = Field(description="Vendor/Seller name", default=None)
    vendor_address: Optional[str] = Field(description="Vendor/Seller address", default=None)
    vendor_tax_id: Optional[str] = Field(description="Vendor tax ID or business number", default=None)

    customer_name: Optional[str] = Field(description="Customer/Buyer name", default=None)
    customer_address: Optional[str] = Field(description="Customer/Buyer address", default=None)
    customer_tax_id: Optional[str] = Field(description="Customer tax ID", default=None)

    items: List[InvoiceItem] = Field(description="List of invoice items", default_factory=list)

    subtotal: Optional[float] = Field(description="Subtotal amount before tax", default=None)
    tax_rate: Optional[float] = Field(description="Tax rate percentage", default=None)
    tax_amount: Optional[float] = Field(description="Tax amount", default=None)
    total_amount: Optional[float] = Field(description="Total amount including tax", default=None)

    currency: Optional[str] = Field(description="Currency code (e.g., USD, EUR)", default="USD")
    payment_terms: Optional[str] = Field(description="Payment terms", default=None)
    notes: Optional[str] = Field(description="Additional notes or comments", default=None)


class AIServiceInterface(ABC):
    """Abstract interface for AI service"""

    @abstractmethod
    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        """Extract structured data from an invoice file"""
        pass


class MockAIService(AIServiceInterface):
    """Mock AI service for testing without API key"""

    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        """Generate mock invoice data for testing"""

        # Generate random but realistic mock data
        mock_invoice_number = f"INV-{random.randint(10000, 99999)}"
        mock_date = datetime.now().strftime("%Y-%m-%d")

        mock_items = [
            InvoiceItem(
                description="Professional Services - Consulting",
                quantity=10,
                unit_price=150.00,
                total=1500.00
            ),
            InvoiceItem(
                description="Software License - Annual",
                quantity=1,
                unit_price=999.00,
                total=999.00
            ),
            InvoiceItem(
                description="Training Workshop - 2 days",
                quantity=2,
                unit_price=500.00,
                total=1000.00
            )
        ]

        subtotal = sum(item.total for item in mock_items)
        tax_rate = 10.0
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount

        return InvoiceData(
            invoice_number=mock_invoice_number,
            invoice_date=mock_date,
            due_date=mock_date,
            vendor_name="Mock Vendor Corp",
            vendor_address="123 Mock Street, Test City, TC 12345",
            vendor_tax_id="XX-1234567",
            customer_name="Test Customer Inc",
            customer_address="456 Test Avenue, Demo City, DC 67890",
            customer_tax_id="YY-7654321",
            items=mock_items,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_amount=total,
            currency="USD",
            payment_terms="Net 30",
            notes="This is mock data for testing purposes"
        )


class GeminiAIService(AIServiceInterface):
    """Real Gemini AI service for invoice processing"""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1,  # Low temperature for consistent extraction
            max_output_tokens=2048
        )

        # Create output parser for structured data
        self.parser = PydanticOutputParser(pydantic_object=InvoiceData)

    def _load_image(self, file_path: str) -> str:
        """Load and encode image to base64"""
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if too large (Gemini has limits)
            max_size = (1024, 1024)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()

    def _load_pdf(self, file_path: str) -> List[str]:
        """Load PDF and convert pages to base64 images"""
        import pypdf
        from pdf2image import convert_from_path

        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=200)
            encoded_images = []

            for img in images[:5]:  # Limit to first 5 pages
                # Convert to RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if needed
                max_size = (1024, 1024)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                encoded_images.append(base64.b64encode(buffered.getvalue()).decode())

            return encoded_images
        except Exception as e:
            # Fallback: try to extract text
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                for page in reader.pages[:5]:
                    text += page.extract_text()
                return [text]  # Return text as single "image"

    @retry(
        retry=retry_if_exception_type((Exception,)),
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        """Extract structured data from an invoice using Gemini"""

        try:
            # Prepare the prompt
            system_prompt = """You are an expert invoice data extractor.
            Extract all relevant information from the invoice image/document.
            Be precise and accurate. If a field is not present, leave it as null.
            For dates, always use YYYY-MM-DD format.
            For currency, use standard 3-letter codes (USD, EUR, etc.).
            Extract ALL line items with their details."""

            format_instructions = self.parser.get_format_instructions()

            # Load the file based on type
            if file_type.lower() == 'pdf':
                file_contents = self._load_pdf(file_path)
            else:
                file_contents = [self._load_image(file_path)]

            # Create messages for each page/image
            messages = [
                SystemMessage(content=system_prompt),
                SystemMessage(content=f"Output Format Instructions:\n{format_instructions}")
            ]

            for content in file_contents:
                if content.startswith('{') or len(content) > 1000:  # Likely text
                    messages.append(HumanMessage(content=f"Extract invoice data from this text:\n{content}"))
                else:  # Base64 image
                    messages.append(HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": "Extract all invoice data from this image:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{content}"
                                }
                            }
                        ]
                    ))

            # Get response from Gemini
            response = await self.llm.ainvoke(messages)

            # Parse the response
            try:
                # Try to parse the structured output
                invoice_data = self.parser.parse(response.content)
                return invoice_data
            except OutputParserException:
                # Fallback: try to parse as JSON directly
                try:
                    # Extract JSON from the response
                    json_str = response.content
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0]
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0]

                    data = json.loads(json_str)
                    return InvoiceData(**data)
                except:
                    # Last resort: return minimal data
                    return InvoiceData(
                        notes=f"Failed to parse response. Raw: {response.content[:500]}"
                    )

        except Exception as e:
            raise Exception(f"Failed to extract invoice data: {str(e)}")


class AIServiceFactory:
    """Factory to create appropriate AI service based on configuration"""

    @staticmethod
    def create() -> AIServiceInterface:
        """Create and return appropriate AI service"""
        if settings.USE_MOCK_AI:
            return MockAIService()
        elif settings.GEMINI_API_KEY:
            return GeminiAIService()
        else:
            # Default to mock if no API key
            return MockAIService()


# Singleton instance
ai_service = AIServiceFactory.create()