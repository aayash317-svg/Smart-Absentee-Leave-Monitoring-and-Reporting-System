FROM python:3.11-slim

WORKDIR /workspace

# Install essential build requirements for ReportLab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy source code and static assets
COPY backend/ ./backend
COPY stitch_smart_absence_erp/ ./stitch_smart_absence_erp

# Set environment variables
ENV PYTHONPATH=/workspace
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
