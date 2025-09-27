#!/bin/bash

# Install Tesseract OCR on Linux (Render)
apt-get update
apt-get install -y tesseract-ocr

# Start FastAPI app
uvicorn service:app --host 0.0.0.0 --port $PORT
