FROM python:3.11-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src

# Expose port
EXPOSE 8080

# Use environment variables for host and port
CMD ["sh", "-c", "uvicorn src.app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8080}"]
