# Dockerfile for DevOps Assignment 3 - Selenium Test Runner
# CSC483 - Spring 2025

# Use Python 3.8 slim image as base
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver using webdriver-manager
RUN pip install --no-cache-dir webdriver-manager \
    && python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

# Copy requirements files
COPY selenium-tests/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY selenium-tests/ /app/selenium-tests/
COPY web-app/ /app/web-app/

# Create necessary directories
RUN mkdir -p /app/screenshots \
    && mkdir -p /app/reports \
    && mkdir -p /app/logs

# Set environment variables for tests
ENV BASE_URL=http://localhost:5000
ENV HEADLESS=true
ENV SCREENSHOTS_DIR=/app/screenshots
ENV REPORTS_DIR=/app/reports

# Create a non-root user
RUN useradd -m -u 1000 testuser \
    && chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Default command
CMD ["python", "/app/selenium-tests/test_suite.py"] 