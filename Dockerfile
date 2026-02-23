FROM python:3.10-slim

WORKDIR /app

# System deps + ffmpeg/ffprobe + postgres client deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Project
COPY . /app

EXPOSE 8000