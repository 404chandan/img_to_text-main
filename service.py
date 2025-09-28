# service.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pytesseract
from PIL import Image, UnidentifiedImageError
import io
import re

# On Linux containers (Render uses Ubuntu), the binary name is "tesseract"
# This works because our Dockerfile installs tesseract and puts it on PATH.
pytesseract.pytesseract.tesseract_cmd = "tesseract"

app = FastAPI(title="Medical Report OCR Extractor")

# CORS (adjust origins as you like)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helper Functions ----------

def ocr_from_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR."""
    # Ensure Pillow can open a variety of formats reliably
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Convert to RGB to avoid mode-related issues
        img = img.convert("RGB")
        # Provide a simple configuration; tweak as needed
        text = pytesseract.image_to_string(img, lang="eng")
    return text

def clean_text(text: str) -> str:
    """Clean common OCR mistakes in medical reports."""
    replacements = {
        "Hemglobin": "Hemoglobin",
        "Hgh": "High",
        "Lw": "Low",
        "mgdl": "mg/dL",
        "gdl": "g/dL",
        "µL": "uL",
    }
    for k, v in replacements.items():
        text = re.sub(re.escape(k), v, text, flags=re.IGNORECASE)
    return text.strip()

# ---------- Health / Root ----------

@app.get("/")
def root():
    return {"status": "ok", "service": "Medical Report OCR Extractor"}

@app.get("/health")
def health():
    return {"ok": True}

# ---------- API Endpoint ----------

@app.post("/extract")
async def extract_text(
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    raw_text = ""
    confidence = 0.8  # default guess for OCR confidence

    if file:
        try:
            contents = await file.read()
            if not contents:
                return {"status": "error", "message": "Empty file received"}
            raw_text = ocr_from_image_bytes(contents)
            confidence = 0.78
        except UnidentifiedImageError:
            return {"status": "error", "message": "Unsupported or corrupt image file"}
        except Exception as e:
            return {"status": "error", "message": f"OCR failed: {str(e)}"}
    elif text_input is not None:
        raw_text = text_input
        confidence = 0.95
    else:
        return {"status": "error", "message": "No input provided"}

    cleaned = clean_text(raw_text)

    return {
        "tests_raw": [ln.strip() for ln in cleaned.splitlines() if ln.strip()],
        "confidence": round(confidence, 2),
        "status": "ok",
    }

# ---------- Run with Uvicorn (local dev) ----------
if __name__ == "__main__":
    import uvicorn
    # Use port 8000 locally; on Render, Dockerfile passes $PORT
    uvicorn.run(app, host="0.0.0.0", port=8000)
