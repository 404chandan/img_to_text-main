# service.py
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import pytesseract
from PIL import Image
import io
import re

# Path to Tesseract OCR binary on Linux (Render uses Ubuntu)
pytesseract.pytesseract.tesseract_cmd = "tesseract"

app = FastAPI(title="Medical Report OCR Extractor")

# ---------- Helper Functions ----------

def ocr_from_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR"""
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    return text

def clean_text(text: str) -> str:
    """Clean common OCR mistakes in medical reports"""
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

# ---------- API Endpoint ----------

@app.post("/extract")
async def extract_text(
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    raw_text = ""
    confidence = 0.8  # default guess for OCR confidence

    if file:
        contents = await file.read()
        raw_text = ocr_from_image_bytes(contents)
        confidence = 0.78
    elif text_input:
        raw_text = text_input
        confidence = 0.95
    else:
        return {"status": "error", "message": "No input provided"}

    cleaned = clean_text(raw_text)

    return {
        "tests_raw": [ln.strip() for ln in cleaned.splitlines() if ln.strip()],
        "confidence": round(confidence, 2),
        "status": "ok"
    }

# ---------- Run with Uvicorn ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
