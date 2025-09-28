# Dockerfile
FROM python:3.11-slim

# System deps: Tesseract OCR + English language + libs for Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        locales && \
    rm -rf /var/lib/apt/lists/*

# Optional locale to avoid warnings
RUN sed -i 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render provides $PORT
ENV PORT=8000
EXPOSE 8000

# Bind to 0.0.0.0 for external access; use $PORT from environment
CMD ["sh", "-c", "uvicorn service:app --host 0.0.0.0 --port ${PORT}"]
