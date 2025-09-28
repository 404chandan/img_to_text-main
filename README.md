# Medical Report OCR Extractor (FastAPI + Tesseract)

## Endpoints
- `GET /` or `GET /health` – health checks
- `POST /extract` – form-data:
  - `text_input` (string) **or**
  - `file` (image: jpg/png/webp/etc.)

## Local Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python service.py
