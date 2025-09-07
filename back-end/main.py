from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Literal
from io import BytesIO
import PyPDF2
import logging

from services.analyzer import analyze_resume, suggest_growth_path, optimize_resume, generate_cover_letter_text
from services.pdf_generator import generate_resume_pdf, generate_resume_bytes


app = FastAPI(title="AI Resume Assistant", version="0.2.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PDF_SIZE_MB = 10


def json_response(success: bool, message: str = "", data: dict | None = None):
    return JSONResponse({"success": success, "message": message, "data": data or {}}, status_code=200 if success else 400)


class AnalyzeRequest(BaseModel):
    resume: str
    job_desc: str


class SuggestRequest(BaseModel):
    resume: str


class DownloadPDFRequest(BaseModel):
    resume: str


class OptimizeRequest(BaseModel):
    resume: str


class CoverLetterRequest(BaseModel):
    resume: str
    job_desc: str


# Simple in-memory preferences
_PREFERENCES: dict[str, str] = {"theme": "light"}

class UserPrefRequest(BaseModel):
    theme: Literal["light", "dark"]


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    logger.info(f"Upload attempt: filename={file.filename}, content_type={file.content_type}")
    
    if file.content_type not in ("application/pdf", "application/x-pdf", "application/octet-stream"):
        logger.warning(f"Invalid file type: {file.content_type}")
        return json_response(False, "Only PDF files are supported")
    
    file_bytes = await file.read()
    if not file_bytes:
        logger.warning("Empty file uploaded")
        return json_response(False, "Uploaded file is empty")
    
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_PDF_SIZE_MB:
        logger.warning(f"File too large: {size_mb:.2f}MB")
        return json_response(False, f"PDF exceeds {MAX_PDF_SIZE_MB} MB")

    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text_parts: List[str] = []
        for page in reader.pages:
            extracted = ""
            try:
                extracted = page.extract_text() or ""
            except Exception:
                pass
            if extracted:
                text_parts.append(extracted)
        resume_text = "\n".join(text_parts).strip()
        if not resume_text:
            logger.warning("No text extracted from PDF")
            return json_response(False, "Could not extract text from PDF. Please upload a text-based PDF.")
        
        logger.info(f"Successfully processed PDF: {len(resume_text)} characters extracted")
        return json_response(True, "Resume uploaded", {"resume_text": resume_text})
    except Exception as exc:
        logger.error(f"PDF processing failed: {exc}")
        return json_response(False, f"Failed to read PDF: {exc}")


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    logger.info(f"Analysis request: resume_length={len(req.resume)}, job_desc_length={len(req.job_desc)}")
    try:
        result = analyze_resume(req.resume, req.job_desc)
        logger.info(f"Analysis complete: match_percent={result.get('match_percent', 0)}")
        return json_response(True, "Analysis complete", result)
    except Exception as exc:
        logger.error(f"Analysis failed: {exc}")
        return json_response(False, f"Analysis failed: {exc}")


@app.post("/suggest")
async def suggest(req: SuggestRequest):
    path = suggest_growth_path(req.resume)
    return json_response(True, "Suggestions ready", path)


@app.post("/optimize_resume")
async def optimize(res: OptimizeRequest):
    optimized = optimize_resume(res.resume)
    return json_response(True, "Resume optimized", {"optimized_resume": optimized})


@app.post("/generate_cover_letter")
async def generate_cover_letter(req: CoverLetterRequest):
    text = generate_cover_letter_text(req.resume, req.job_desc)
    return json_response(True, "Cover letter generated", {"cover_letter": text})


@app.post("/download_pdf")
async def download_pdf(req: DownloadPDFRequest, format: Literal["pdf", "docx", "txt"] = Query("pdf")):
    try:
        file_bytes, media_type, filename = generate_resume_bytes(req.resume, format)
    except Exception as exc:
        return json_response(False, f"Failed to generate file: {exc}")
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@app.post("/user/preferences")
async def set_preferences(req: UserPrefRequest):
    _PREFERENCES["theme"] = req.theme
    return json_response(True, "Preferences saved", {"theme": _PREFERENCES["theme"]})


# Health endpoint (optional for quick checks)
@app.get("/health")
async def health():
    return json_response(True, "ok", {"status": "ok"})

# Test endpoint for debugging
@app.get("/test")
async def test():
    return {"message": "Backend is working!", "timestamp": "2024-01-01"}
