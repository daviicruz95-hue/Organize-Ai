FROM python:3.11-slim

# Install system dependencies (curl, ffmpeg) and Node.js 20
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install WhatsApp service npm dependencies
COPY whatsapp-service/package*.json ./whatsapp-service/
RUN cd whatsapp-service && npm install --production

# Copy application source code
COPY . .

# Ensure start script is executable
RUN chmod +x start.sh

# Environment variables
ENV PORT=5050
ENV PYTHONUNBUFFERED=1

EXPOSE 5050

CMD ["./start.sh"]
