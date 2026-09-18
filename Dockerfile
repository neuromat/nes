FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Run the application
CMD ["python", "app.py"]