## Bugs & Fixes

| Bug / Issue | Cause | How it was fixed / Resolution | Notes / Outcome |
|------------|-------|-------------------------------|----------------|
| Agents failed to initialize properly | Manual creation of agents with detailed roles caused version conflicts. | Simplified initialization with `Agent(name="...")` in `try/except`. | Prevents runtime crashes if CrewAI agents fail. |
| CrewAI version conflicts | `crewai` and `crewai-tools` conflicted with other packages. | Installed base dependencies first, then force-installed critical packages without dependency resolution. | Resolves dependency conflicts and allows successful build. |
| File handling and PDF extraction issues | Missing libraries or unsupported files caused crashes. | Added try/except for PDF import, and a universal `extract_text()` function for `pdf`, `txt`, `csv`. | Safe text extraction without crashing. |
| FastAPI endpoints blocked by long-running tasks | Synchronous Crew tasks blocked the server. | Moved processing to **Celery async tasks**. | Server remains responsive. |
| Database missing / no persistence | Old code stored everything in-memory. | Added **SQLAlchemy** models to persist analysis results. | Data is tracked and retrievable even after restart. |
| No status tracking | Users couldn’t check task progress. | Added `/status/{analysis_id}` and `/results/{analysis_id}` endpoints. | Users can see queued, processing, failed, or completed status. |
| Environment variable issues (OPENAI_API_KEY) | Missing API key caused crashes. | Added fallback with default summary and message. | Safe handling; no crashes if key is missing. |
| Unsupported file extensions | Users could upload non-supported file types. | Allowed only `pdf`, `txt`, `csv`. | Prevents crashes and invalid file processing. |
| Docker / deployment issues | Conflicting system dependencies and packages. | Installed system packages first, installed Python packages in controlled order with `--no-deps`. | Clean Docker build with Postgres + Redis + FastAPI + Celery. |
| Missing CORS handling | Frontend requests blocked by browser. | Added `CORSMiddleware`. | Frontend can call API safely. |
| Text extraction errors / crashes | PDFs or CSV/TXT had encoding issues or unreadable pages. | Added error handling in extraction functions. | Extracts whatever possible and reports errors safely. |
| Hardcoded paths and cleanup issues | Fixed paths and unsafe file deletion caused crashes. | Created `data/` directory if missing and used `try/except` for file removal. | Prevents crashes during cleanup. |
| OpenAI call failures | API errors crashed the server. | Wrapped OpenAI calls in `try/except`, returned defaults if failed. | Resilient AI analysis without breaking the server. |
| Complex CrewAI task hallucinations | Old `Task` definitions made AI produce contradictory output. | Replaced with structured OpenAI GPT prompt for financial analysis. | More reliable and readable financial summaries. |




# 🟢 Financial Analyzer API

A financial document analyzer using FastAPI, Celery, Redis, Postgres, and OpenAI GPT.  
It can summarize PDFs/TXT/CSV financial reports, provide risks, and recommend BUY/HOLD/SELL.

---

## 📦 Requirements

- Docker & Docker Compose installed
- OpenAI API key

---

## 1️⃣ Unzip the Project

- Download the zip file.  
- Extract it to a folder, e.g., `financial-analyzer/`.  

---


4️⃣ Access the API

OpenAPI docs: http://localhost:8000/docs

Upload a financial document
POST /analyze


## Access the API
- **OpenAPI docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Upload a financial document:** `POST /analyze`


# File Upload Form

Upload a PDF, TXT, or CSV file with optional query and company name.

## Fields
- **File** (required): PDF, TXT, or CSV file.
- **Query** (optional): Related query text.
- **Company Name** (optional): Name of the company.


- **Upload a financial document:** `POST /analyze`
- **Check status:** `GET /status/{analysis_id}`
- **Get results:** `GET /results/{analysis_id}`

## 2️⃣ Set Up Environment Variables

- Inside the project folder, create a `.env` file.  
- Add the following:


```env
# Database
POSTGRES_DB=financial_analyzer
POSTGRES_USER=financial_user
POSTGRES_PASSWORD=vai
DATABASE_URL=postgresql://financial_user:vai@postgres:5432/financial_analyzer

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# FastAPI port
PORT=8000


