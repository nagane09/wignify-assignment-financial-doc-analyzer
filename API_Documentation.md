==========================================================
                FINANCIAL DOCUMENT ANALYZER API
==========================================================

Description:
-------------
This API allows users to upload financial documents (PDF, TXT, CSV)
and receive automated investment analysis using OpenAI GPT models.
It supports asynchronous processing with Celery and stores results
in a database.

Base URL:
---------
http://<your-server-domain-or-ip>:8000

==========================================================
Endpoints:
----------

1. Health Check
---------------
GET /

Description: Check if the API is running.

Response:
{
    "message": "Financial Document Analyzer API is running"
}

----------------------------------------------------------

2. Analyze Document
------------------
POST /analyze

Description: Upload a financial document for analysis.
             Analysis is queued for asynchronous processing.

Request Parameters (multipart/form-data):
    file          : PDF, TXT, or CSV file (required)
    query         : Query for analysis (optional, default: "Analyze this financial document")
    company_name  : Name of the company in the document (optional, default: "Unknown")

Response:
{
    "analysis_id": "uuid-string",
    "status": "queued"
}

----------------------------------------------------------

3. Check Analysis Status
-----------------------
GET /status/{analysis_id}

Description: Check processing status of a previously submitted document.

Path Parameters:
    analysis_id : The ID returned from /analyze (required)

Response (Queued or Processing):
{
    "status": "queued",
    "error": null
}

Response (Failed):
{
    "status": "failed",
    "error": "Error message if processing failed"
}

----------------------------------------------------------

4. Retrieve Analysis Results
----------------------------
GET /results/{analysis_id}

Description: Retrieve the final analysis once processing is completed.

Path Parameters:
    analysis_id : The ID returned from /analyze (required)

Response (Completed):
{
    "report_preview": "First 10,000 characters of the document",
    "full_analysis": {
        "summary": "Summary of the financial document",
        "recommendation": "BUY / HOLD / SELL",
        "confidence": 0.7,
        "risks": ["High debt mentioned", "Legal issues mentioned"],
        "market_insights": "Generated using OpenAI GPT"
    },
    "company_name": "Company XYZ",
    "query": "Analyze this financial document",
    "extracted_characters": 12345
}

Response (Still processing):
{
    "detail": "Still processing"
}

Response (Invalid ID):
{
    "detail": "Invalid ID"
}

==========================================================
Supported File Types:
---------------------
- PDF (.pdf)
- Text (.txt)
- CSV (.csv)

Unsupported file types return a 400 error.

==========================================================
Notes:
------
- Analysis runs asynchronously using Celery.
- Results are stored in the database (PostgreSQL or SQLite).
- Ensure OPENAI_API_KEY is set in .env for GPT analysis.
- Only the first 10,000 characters of large documents are included in the preview.
- Recommended environment: Python >= 3.11

