# Financial Analyzer API

A FastAPI application that allows uploading financial documents (PDF, TXT, CSV) for automated analysis using OpenAI GPT. Analysis is processed asynchronously via Celery, and results can be retrieved via API endpoints.

---

## Table of Contents
- [Form Fields](#form-fields)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Setup](#setup)
- [Usage Examples](#usage-examples)
- [Celery Task](#celery-task)
- [Notes](#notes)

---

## Form Fields

The API accepts file uploads with optional query and company name fields:

| Field          | Type         | Required | Description |
|----------------|-------------|----------|-------------|
| `file`         | PDF/TXT/CSV | Yes      | Upload the financial document. |
| `query`        | Text        | No       | Optional query related to the document. Default: `"Analyze this financial document"` |
| `company_name` | Text        | No       | Optional company name. Default: `"Unknown"` |

---

## API Endpoints

### 1. Upload a financial document
- **Endpoint:** `POST /analyze`
- **Description:** Upload a document for analysis. Returns a unique `analysis_id`.
- **Request:** `multipart/form-data`
- **Response:**
```json
{
  "analysis_id": "uuid-string",
  "status": "queued"
}

```



### 2. Check Analysis Status

Endpoint: GET /status/{analysis_id}

Description: Check the processing status of a document.

Response:

{
  "status": "queued|processing|completed|failed",
  "error": "Error message if failed"
}

3. Get Analysis Results

Endpoint: GET /results/{analysis_id}

Description: Retrieve the completed analysis results.

Response:

{
  "report_preview": "First 10,000 chars of extracted text",
  "full_analysis": {
    "summary": "Short summary of the document",
    "recommendation": "BUY|HOLD|SELL",
    "confidence": 0.7,
    "risks": ["High debt mentioned.", "Legal issues mentioned."],
    "market_insights": "Generated using OpenAI GPT"
  },
  "company_name": "Optional company name",
  "query": "Optional query",
  "extracted_characters": 12345
}

4. OpenAPI Documentation

URL: http://localhost:8000/docs
