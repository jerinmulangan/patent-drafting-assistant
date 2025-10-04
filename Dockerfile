# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TMPDIR=/tmp

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt . 

# Install pip first and heavy dependencies separately
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir numpy pandas faiss-cpu sentence-transformers \
    && pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
