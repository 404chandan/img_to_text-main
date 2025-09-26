# service_extract.py
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import pytesseract
from PIL import Image
import io
import re

# Path to Tesseract OCR binary (update if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI(title="Medical Report OCR Extractor")

# ---------- Helper Functions ----------

# OCR from image
def ocr_from_image_bytes(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    return text

# Clean up text (fix common OCR mistakes)
def clean_text(text: str) -> str:
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
async def extract_text(text_input: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
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

    # Output only Step 1 result
    return {
        "tests_raw": [ln.strip() for ln in cleaned.splitlines() if ln.strip()],
        "confidence": round(confidence, 2),
        "status": "ok"
    }
