FROM python:3.11-slim-bullseye

# Add Debian backports for newer FFmpeg
RUN echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list

# Update and install all dependencies
RUN apt-get update && apt-get install -y -t bullseye-backports \
    ffmpeg \
    && apt-get install -y \
    build-essential \
    pkg-config \
    git \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install Python packages one by one to isolate issues
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy==1.24.3 && \
    pip install --no-cache-dir scipy==1.15.3 && \
    pip install --no-cache-dir scikit-learn==1.3.2 && \
    pip install --no-cache-dir fastapi==0.104.1 && \
    pip install --no-cache-dir uvicorn[standard]==0.24.0 && \
    pip install --no-cache-dir python-multipart==0.0.6 && \
    pip install --no-cache-dir ollama==0.1.8 && \
    pip install --no-cache-dir pydantic==2.5.0 && \
    pip install --no-cache-dir python-dotenv==1.0.0 && \
    pip install --no-cache-dir ctranslate2==4.7.1 && \
    pip install --no-cache-dir faster-whisper==0.10.0

COPY . .

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT