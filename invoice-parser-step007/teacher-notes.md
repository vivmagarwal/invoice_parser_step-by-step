# Teacher Notes - STEP 007: AI Integration with Gemini API

## Learning Objectives
By the end of this step, students will be able to:
1. ✅ Set up Google Gemini API for AI processing
2. ✅ Implement LangChain for structured output parsing
3. ✅ Handle AI errors gracefully with retries
4. ✅ Create mock services for testing without API keys
5. ✅ Process images and PDFs with AI
6. ✅ Extract structured data from unstructured documents

## Prerequisites
- Completed Step 006 (File Upload System)
- Basic understanding of async/await
- Understanding of API integration
- Familiarity with JSON data structures

## Time Estimate
- **Teaching**: 3-4 hours
- **Practice**: 2-3 hours
- **Total**: 5-7 hours

## Setup Instructions

### 1. Environment Setup
```bash
# Navigate to the step directory
cd invoice-parser-step007/ending-code/backend

# Create virtual environment if not exists
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add these settings to `.env`:
```env
# For testing with mock AI (no API key needed)
USE_MOCK_AI=true

# For real AI (get key from https://makersuite.google.com/app/apikey)
# GEMINI_API_KEY=your-actual-api-key-here
# USE_MOCK_AI=false
```

### 3. Run the Application
```bash
# Terminal 1: Run backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8007

# Terminal 2: Run frontend (optional for this step)
cd frontend
npm install
npm run dev
```

## Testing the Implementation

### Manual Testing Guide

#### 1. Test Mock AI Service (No API Key Required)
```bash
# Run the test script
cd backend
python test_step007.py
```

Expected output:
```
============================================================
STEP-007: AI Integration Test
============================================================

1. Registering test user...
✓ User registered: aitest

2. Logging in...
✓ Logged in successfully

3. Creating sample invoice image...
✓ Sample invoice image created

4. Uploading invoice...
✓ Invoice uploaded with ID: 1
  Status: pending
  File: test_invoice.png

5. Processing invoice with AI...
  Note: Using mock AI service for testing
✓ Invoice processed successfully
  Status: completed

6. Retrieving processed invoice...
✓ Invoice data retrieved
  Status: completed

  Extracted Data:
    Invoice Number: INV-12345
    Vendor: Mock Vendor Corp
    Customer: Test Customer Inc
    Total Amount: $3499.0
    Currency: USD

    Line Items (3 items):
      - Professional Services - Consulting: $1500.0
      - Software License - Annual: $999.0
      - Training Workshop - 2 days: $1000.0

7. Testing error handling...
✓ Correctly prevented reprocessing
✓ Correctly handled non-existent invoice

8. Listing all invoices...
✓ Found 1 invoice(s)
  - ID: 1, Status: completed, File: test_invoice.png
```

#### 2. Test with cURL Commands
```bash
# 1. Register a user
curl -X POST http://localhost:8007/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "testpass123"
  }'

# 2. Login
curl -X POST http://localhost:8007/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"

# Save the access token from response
TOKEN="your-access-token-here"

# 3. Upload an invoice
curl -X POST http://localhost:8007/api/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_invoice.png"

# 4. Process the invoice (replace {id} with actual ID)
curl -X POST http://localhost:8007/api/invoices/{id}/process \
  -H "Authorization: Bearer $TOKEN"

# 5. Get processed data
curl -X GET http://localhost:8007/api/invoices/{id} \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Test with Real Gemini API
1. Get API key from https://makersuite.google.com/app/apikey
2. Update `.env` file:
   ```env
   GEMINI_API_KEY=your-actual-key-here
   USE_MOCK_AI=false
   ```
3. Restart the server
4. Run the same tests - now with real AI processing

### Verification Checklist
- [ ] Mock AI service returns structured data
- [ ] Invoice status changes: pending → processing → completed
- [ ] Extracted data is stored in database
- [ ] Error handling prevents reprocessing
- [ ] 404 returned for non-existent invoices
- [ ] API documentation shows new `/process` endpoint
- [ ] Real Gemini API works when configured (optional)

## Common Issues and Solutions

### Issue 1: ImportError for LangChain
**Error:**
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution:**
```bash
pip install langchain langchain-google-genai langchain-core
```

### Issue 2: Gemini API Key Error
**Error:**
```
ValueError: GEMINI_API_KEY not configured
```
**Solution:**
Either:
1. Set `USE_MOCK_AI=true` in `.env` for testing, or
2. Get API key and set `GEMINI_API_KEY=your-key` in `.env`

### Issue 3: PDF Processing Error
**Error:**
```
ImportError: cannot import name 'convert_from_path'
```
**Solution:**
```bash
# Install poppler (required for pdf2image)
# macOS:
brew install poppler

# Ubuntu/Debian:
sudo apt-get install poppler-utils

# Then reinstall pdf2image:
pip install pdf2image
```

### Issue 4: Pydantic Version Conflict
**Error:**
```
ImportError: cannot import name 'BaseModel' from 'langchain_core.pydantic_v1'
```
**Solution:**
```bash
pip install --upgrade pydantic langchain-core
```

### Issue 5: Async Context Error
**Error:**
```
RuntimeError: This event loop is already running
```
**Solution:**
Make sure all AI service methods are properly async/await. Check that invoice processing is awaited.

## Key Concepts Explained

### 1. AI Service Architecture
```python
# Abstract interface for flexibility
class AIServiceInterface(ABC):
    @abstractmethod
    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        pass

# Mock implementation for testing
class MockAIService(AIServiceInterface):
    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        # Returns realistic mock data
        return InvoiceData(...)

# Real implementation with Gemini
class GeminiAIService(AIServiceInterface):
    async def extract_invoice_data(self, file_path: str, file_type: str) -> InvoiceData:
        # Uses Gemini API for real extraction
        ...

# Factory pattern for service selection
class AIServiceFactory:
    @staticmethod
    def create() -> AIServiceInterface:
        if settings.USE_MOCK_AI:
            return MockAIService()
        elif settings.GEMINI_API_KEY:
            return GeminiAIService()
        else:
            return MockAIService()  # Fallback
```

### 2. Structured Output with LangChain
```python
# Define expected structure with Pydantic
class InvoiceData(BaseModel):
    invoice_number: Optional[str] = Field(description="Invoice number")
    vendor_name: Optional[str] = Field(description="Vendor name")
    items: List[InvoiceItem] = Field(description="Line items")
    total_amount: Optional[float] = Field(description="Total amount")

# Create parser for structured extraction
parser = PydanticOutputParser(pydantic_object=InvoiceData)

# Use parser with LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
format_instructions = parser.get_format_instructions()
response = await llm.ainvoke(messages)
invoice_data = parser.parse(response.content)
```

### 3. Error Handling with Retries
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    retry=retry_if_exception_type((Exception,)),
    wait=wait_exponential(min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
async def extract_invoice_data(self, file_path: str, file_type: str):
    # AI processing with automatic retries
    ...
```

### 4. Status Management
```python
# Invoice processing flow
async def process_invoice(db: AsyncSession, invoice_id: int, user_id: int):
    # 1. Check current status
    if invoice.status != InvoiceStatus.pending:
        raise HTTPException(400, "Already processed")

    # 2. Update to processing
    invoice.status = InvoiceStatus.processing
    await db.commit()

    try:
        # 3. Extract data
        data = await ai_service.extract_invoice_data(...)

        # 4. Update to completed
        invoice.status = InvoiceStatus.completed
        invoice.extracted_data = data.model_dump_json()
        await db.commit()

    except Exception as e:
        # 5. Update to failed
        invoice.status = InvoiceStatus.failed
        invoice.error_message = str(e)
        await db.commit()
        raise
```

## Assessment Points

### Basic Understanding (Must Pass)
1. **Q:** Why use an interface for AI service?
   **A:** Allows switching between mock and real implementations without changing code

2. **Q:** What is LangChain used for?
   **A:** Structured output parsing - converting AI responses to Pydantic models

3. **Q:** Why implement retry logic?
   **A:** AI APIs can be unreliable; retries improve robustness

### Intermediate Understanding
1. **Q:** How does the factory pattern help here?
   **A:** Centralizes service creation logic; easy configuration-based switching

2. **Q:** What happens if AI extraction fails?
   **A:** Status set to 'failed', error message stored, HTTP 500 returned

3. **Q:** Why store both raw JSON and extracted fields?
   **A:** JSON has all data; fields allow quick database queries

### Advanced Understanding
1. **Q:** How would you add OpenAI as an alternative?
   **A:** Create OpenAIService implementing AIServiceInterface, update factory

2. **Q:** How to handle partial extraction failure?
   **A:** Return what was extracted, mark specific fields as null, add notes

3. **Q:** How to implement caching for AI results?
   **A:** Check if similar file processed before, reuse extraction if match found

## Extensions and Challenges

### Challenge 1: Add OpenAI Support
```python
class OpenAIService(AIServiceInterface):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_invoice_data(self, file_path: str, file_type: str):
        # Implement OpenAI Vision API integration
        pass
```

### Challenge 2: Confidence Scores
```python
class InvoiceData(BaseModel):
    invoice_number: Optional[str]
    invoice_number_confidence: Optional[float]  # 0.0 to 1.0
    # Add confidence for each field
```

### Challenge 3: Multi-Language Support
```python
async def extract_invoice_data(self, file_path: str, file_type: str, language: str = "en"):
    # Adjust prompts based on language
    # Return results in requested language
```

### Challenge 4: Batch Processing
```python
@router.post("/batch-process")
async def batch_process_invoices(
    invoice_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Process multiple invoices concurrently
    tasks = [process_invoice(db, id, current_user.id) for id in invoice_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Connection to Next Steps

### What We've Built
- AI service abstraction layer
- Structured data extraction
- Mock service for testing
- Error handling and retries
- Status tracking system

### Preparing for Step 008
Next, we'll implement complete invoice processing:
- Store extracted data in dedicated tables
- Create relationships between entities
- Build data validation pipeline
- Implement business rules

### Key Takeaways
1. **Abstraction**: Interfaces allow flexibility
2. **Testing**: Mock services enable development without API keys
3. **Resilience**: Retries and error handling are crucial
4. **Structure**: LangChain helps parse AI output reliably
5. **Status**: Track processing states for user feedback

## Resources

### Documentation
- [Google Gemini API](https://ai.google.dev/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [Tenacity Retry Library](https://tenacity.readthedocs.io/)

### Example Invoices for Testing
- [Sample Invoices Dataset](https://www.kaggle.com/datasets/tonygordonjr/invoice-dataset)
- [Invoice Templates](https://www.invoicesimple.com/invoice-template)

### Troubleshooting Guide
1. Check `.env` file configuration
2. Verify all dependencies installed
3. Ensure database migrations applied
4. Check file upload directory exists
5. Verify API key validity (if using real AI)

## Final Checklist

### Student Should Be Able To:
- [ ] Explain AI service abstraction pattern
- [ ] Configure Gemini API credentials
- [ ] Test with mock AI service
- [ ] Process an invoice through API
- [ ] Handle processing errors gracefully
- [ ] View extracted data in response
- [ ] Understand status transitions
- [ ] Debug common issues

### Files Modified/Created:
- `app/services/ai_service.py` - NEW: AI service implementations
- `app/services/invoice_service.py` - MODIFIED: Added process_invoice method
- `app/api/invoices.py` - MODIFIED: Added /process endpoint
- `app/core/config.py` - MODIFIED: Added AI configuration
- `requirements.txt` - MODIFIED: Added AI dependencies
- `.env.example` - MODIFIED: Added AI settings
- `test_step007.py` - NEW: Comprehensive test script

### Next Session Prep:
1. Review database relationships (one-to-many, many-to-many)
2. Think about data validation requirements
3. Consider what business rules might apply
4. Plan for handling extracted data storage

---

**Remember**: The goal is not just to integrate AI, but to understand how to build flexible, testable systems that can work with or without external services. The patterns learned here apply to any third-party API integration.