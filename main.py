# -------------------------
# Imports and environment
# -------------------------
import os
import uuid
import json
import traceback
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from celery import Celery
import uvicorn

from dotenv import load_dotenv
load_dotenv()  # loads .env

# Optional: PyPDF2 for PDFs
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# OpenAI
import openai

# -------------------------
# Database setup
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")
if DATABASE_URL.startswith("postgres"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# -------------------------
# Celery setup
# -------------------------
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "financial_analyzer",
    broker=redis_url,
    backend=redis_url
)
celery_app.conf.update(task_track_started=True)

# -------------------------
# Database model
# -------------------------
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    company_name = Column(String, nullable=True)
    status = Column(String, default="pending")
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# -------------------------
# FastAPI setup
# -------------------------
app = FastAPI(title="Financial Analyzer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# -------------------------
# Text extraction functions
# -------------------------
def extract_text_from_pdf(path: str) -> str:
    if PdfReader is None:
        return "PDF extraction not available (PyPDF2 missing)."
    try:
        text_parts = []
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                ptxt = page.extract_text()
                if ptxt:
                    text_parts.append(ptxt)
        return "\n".join(text_parts)
    except Exception as e:
        return f"PDF read error: {e}"

def extract_text_from_csv(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"CSV read error: {e}"

def extract_text_from_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"TXT read error: {e}"

def extract_text(path: str) -> str:
    ext = path.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(path)
    elif ext == "csv":
        return extract_text_from_csv(path)
    elif ext == "txt":
        return extract_text_from_txt(path)
    else:
        return f"Unsupported file extension: {ext}"

# -------------------------
# OpenAI analysis
# -------------------------
def openai_analyze(text: str, query: str, company_name: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "summary": text[:2000],
            "recommendation": "HOLD",
            "confidence": 0.2,
            "risks": [],
            "market_insights": "OPENAI_API_KEY missing."
        }
    try:
        openai.api_key = api_key
        prompt = f"Analyze the financial document for {company_name}:\n\n{text}\n\nProvide a short summary, main risks, and a BUY/HOLD/SELL recommendation."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        result_text = response.choices[0].message.content

        rec = "HOLD"
        lower = result_text.lower()
        if "buy" in lower:
            rec = "BUY"
        elif "sell" in lower:
            rec = "SELL"

        risks = []
        if "debt" in lower:
            risks.append("High debt mentioned.")
        if "lawsuit" in lower or "litigation" in lower:
            risks.append("Legal issues mentioned.")

        return {
            "summary": result_text[:2000],
            "recommendation": rec,
            "confidence": 0.7,
            "risks": risks,
            "market_insights": "Generated using OpenAI GPT"
        }
    except Exception as e:
        return {
            "summary": text[:2000],
            "recommendation": "HOLD",
            "confidence": 0.1,
            "risks": [f"OpenAI error: {str(e)}"],
            "market_insights": "OpenAI call failed."
        }

# -------------------------
# Celery Task
# -------------------------
@celery_app.task(bind=True)
def process_financial_document(self, analysis_id, file_path, query, company_name):
    db = SessionLocal()
    entry = None
    try:
        entry = db.query(AnalysisResult).filter_by(id=analysis_id).first()
        if not entry:
            return
        entry.status = "processing"
        db.commit()

        extracted_text = extract_text(file_path)
        MAX_PREVIEW = 10000
        preview = extracted_text[:MAX_PREVIEW]

        analysis = openai_analyze(extracted_text, query, company_name)

        result_payload = {
            "report_preview": preview,
            "full_analysis": analysis,
            "company_name": company_name,
            "query": query,
            "extracted_characters": len(extracted_text)
        }

        entry.status = "completed"
        entry.result = result_payload
        entry.completed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        tb = traceback.format_exc()
        if entry:
            entry.status = "failed"
            entry.error_message = f"{str(e)}\n{tb}"
            entry.completed_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

# -------------------------
# FastAPI endpoints
# -------------------------
@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form("Analyze this financial document"),
    company_name: str = Form("Unknown"),
    db: Session = Depends(get_db)
):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "txt", "csv"]:
        raise HTTPException(400, "Only PDF, TXT, CSV allowed")

    analysis_id = str(uuid.uuid4())
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{analysis_id}.{ext}"

    with open(file_path, "wb") as out:
        out.write(await file.read())

    entry = AnalysisResult(
        id=analysis_id,
        filename=file.filename,
        query=query,
        company_name=company_name,
        status="queued"
    )
    db.add(entry)
    db.commit()

    process_financial_document.delay(analysis_id, file_path, query, company_name)
    return {"analysis_id": analysis_id, "status": "queued"}

@app.get("/status/{analysis_id}")
def status(analysis_id: str, db: Session = Depends(get_db)):
    result = db.query(AnalysisResult).filter_by(id=analysis_id).first()
    if not result:
        raise HTTPException(404, "Invalid ID")
    return {"status": result.status, "error": result.error_message}

@app.get("/results/{analysis_id}")
def results(analysis_id: str, db: Session = Depends(get_db)):
    result = db.query(AnalysisResult).filter_by(id=analysis_id).first()
    if not result:
        raise HTTPException(404, "Invalid ID")
    if result.status != "completed":
        raise HTTPException(400, "Still processing")
    return result.result

# -------------------------
# Run FastAPI
# -------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
