# Invoice Parser

AI-powered invoice processing system with database persistence, built with FastAPI and Google Gemini.

## 🚀 Features

- **AI-Powered Extraction**: Uses Google Gemini 2.0 Flash for accurate data extraction
- **Database Persistence**: PostgreSQL storage with full relationship mapping
- **Modern API**: FastAPI with automatic documentation and validation
- **Modular Architecture**: Clean separation of concerns for maintainability
- **GST Compliance**: Specifically designed for Indian GST-compliant invoices
- **Web Interface**: Responsive HTML interface with drag-and-drop upload

## 📋 Requirements

- Python 3.13+
- PostgreSQL database (Neon recommended)
- Google Gemini API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invoice_parser
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   # or with uv
   uv pip install -e .
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set environment variables**
   ```env
   DATABASE_URL=postgresql://user:password@host/database
   GOOGLE_API_KEY=your_gemini_api_key
   ```

## 🚀 Usage

### Start the Server

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### API Endpoints

#### Process Invoice
```bash
curl -X POST "http://localhost:8000/api/parse-invoice" \
  -F "file=@invoice.jpg"
```

#### Save to Database
```bash
curl -X POST "http://localhost:8000/api/save-invoice" \
  -H "Content-Type: application/json" \
  -d @invoice_data.json
```

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application entry point
├── models/
│   ├── schemas.py       # Pydantic models (API schemas)
│   └── database.py      # SQLAlchemy models
├── core/
│   ├── config.py        # Configuration management
│   ├── database.py      # Database connection
│   └── ai_processor.py  # AI processing logic
├── api/
│   ├── dependencies.py  # Dependency injection
│   └── routes/          # API route handlers
├── services/
│   ├── invoice_service.py    # Business logic
│   └── database_service.py   # Database operations
```

## 🔧 Configuration

Environment variables in `.env`:

```env
# Application
APP_NAME=Invoice Parser
ENVIRONMENT=development
DEBUG=false

# Database
DATABASE_URL=postgresql://...
DB_POOL_SIZE=5

# AI Configuration  
GOOGLE_API_KEY=your_key_here
AI_MODEL_NAME=gemini-2.0-flash

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
```

## 📊 Database Schema

- **invoices**: Main invoice records
- **companies**: Vendor/customer information
- **addresses**: Company address details
- **line_items**: Invoice line items
- **tax_calculations**: GST tax breakdowns

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Test file upload
curl -X POST http://localhost:8000/api/parse-invoice \
  -F "file=@test_invoice.jpg"
```

## 📝 Development

### Project Structure
- Follow the modular architecture pattern
- Services handle business logic
- Routes handle HTTP concerns only
- Models define data structures

### Adding New Features
1. Add models in `app/models/`
2. Implement business logic in `app/services/`
3. Create API routes in `app/api/routes/`
4. Update dependencies in `app/api/dependencies.py`

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Direct Deployment
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📈 Performance

- **Connection Pooling**: Optimized database connections
- **Async Processing**: Non-blocking invoice processing
- **Caching**: Service instances cached for performance
- **Modular Loading**: Only load required components

## 🔒 Security

- Input validation on all endpoints
- File type and size restrictions
- SQL injection prevention via ORM
- Environment variable configuration

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the health check at `/api/health`
- Check application logs for errors
