FROM python:3.11-slim

# Prevent python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for curl and security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data files
COPY . .

# Create unprivileged non-root user and adjust permissions
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/sh -m appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8081

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8081/health || exit 1

CMD ["python", "app.py"]
