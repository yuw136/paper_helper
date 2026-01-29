# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Install system dependencies including LaTeX
# Using lightweight LaTeX packages to keep image size manageable
RUN apt-get update && apt-get install -y --no-install-recommends \
    # LaTeX distribution for PDF generation
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-extra \
    # Additional utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY server/requirements.txt ./server/

# Install Python dependencies
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p server/uploads server/data server/reports

# Expose port 8000
EXPOSE 8000

# Set environment variable to prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Working directory for the app
WORKDIR /app/server

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the server
CMD ["python", "run_server.py"]
